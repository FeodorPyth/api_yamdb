import random

from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import AUTHENTICATION_EMAIL
from .permissions import IsAdminOrReadOnly, IsAdminPermission
from reviews.models import MyUser, Genre, Category, Title
from .serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserAdminSerializer,
    UserSerializer,
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
)
from .viewsets import CreateListDestroyViewSet


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class SignUpAPIView(views.APIView):
    '''
    Вьюсет для получения кода подтверждения:
    POST-запрос с полями username, email
    генерирует email с confirmation_code.
    '''
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer
    queryset = MyUser.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            email = serializer.data['email']
            try:
                user, created = MyUser.objects.get_or_create(
                    username=username,
                    email=email,
                )
            except IntegrityError:
                return Response(
                    'Такой логин или email уже существуют',
                    status=status.HTTP_400_BAD_REQUEST
                )
            confirmation_code = ''.join(
                [str(random.randint(0, 9)) for _ in range(5)]
            )
            MyUser.objects.filter(username=username).update(
                confirmation_code=confirmation_code
            )
            send_mail(
                subject='Confirmation code',
                message=f'''Hello, your code
                is {confirmation_code}!''',
                from_email=AUTHENTICATION_EMAIL,
                recipient_list=[serializer.data['email']],
                fail_silently=False,
            )
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(views.APIView):
    '''
    Вьюсет для получения токена:
    POST-запрос с полями username, confirmation_code
    генерирует jwt-token.
    '''
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                MyUser,
                username=serializer.data['username']
            )
            if serializer.data['confirmation_code'] == user.confirmation_code:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {'token': str(refresh.access_token)},
                    status=status.HTTP_200_OK
                )
            Response('Проверьте правильность введенных данных!',
                     status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для users для администраторов:
    GET-запрос - получение списка пользователей;
    POST-запрос - добавляет нового пользователя;
    GET, PATCH, DELETE-запрос - получение,
    частичное изменение, удаление пользователя по его username.
    '''
    queryset = MyUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(detail=False,
            methods=['get', 'patch'],
            url_path='me',
            url_name='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UserSerializer)
    def users_me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
