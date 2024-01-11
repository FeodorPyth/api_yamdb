import random

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import AUTHENTICATION_EMAIL, URL_PATH_NAME
from .filters import TitleViewSetFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAdmin,
    IsAuthorOrModerOrAdmin
)
from reviews.models import (
    Category,
    Genre,
    MyUser,
    Review,
    Title
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserAdminSerializer,
    UserSerializer,
)


class BaseCategoryGenreViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вьюсет для Категорий и Жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(BaseCategoryGenreViewset):
    """
    Вьюсет для категорий.
    GET-запрос - получение списка категорий.
    POST-запрос - добавляет новую категорию.
    DELETE-запрос - удаление категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewset):
    """
    Вьюсет для жанров.
    GET-запрос - получение списка жанров.
    POST-запрос - добавляет новый жанр.
    DELETE-запрос - удаление жанра.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для произведений.
    GET-запрос - получение списка произведений.
    GET-запрос по id получение конкретного произведения.
    POST-запрос - добавляет новое произведение.
    PATCH-запрос - частичное обновление произведения.
    DELETE-запрос - удаление произведения.
    """
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleViewSetFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для отзывов.
    GET-запрос - получение списка отзывов.
    GET-запрос по id получение конкретного отзыва.
    POST-запрос - добавляет новый отзыв.
    PATCH-запрос - частичное обновление отзыва.
    DELETE-запрос - удаление отзыва.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModerOrAdmin,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для комментариев.
    GET-запрос - получение списка комментариев.
    GET-запрос по id получение конкретного комментария.
    POST-запрос - добавляет новый комментарий.
    PATCH-запрос - частичное обновление комментария.
    DELETE-запрос - удаление комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerOrAdmin,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class SignUpAPIView(views.APIView):
    """
    Вьюсет для получения кода подтверждения.
    POST-запрос генерирует email с confirmation_code.
    """
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer
    queryset = MyUser.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
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
                subject='Код подтверждения',
                message=f'Ваш код: {confirmation_code}!',
                from_email=AUTHENTICATION_EMAIL,
                recipient_list=[serializer.data['email']],
                fail_silently=False,
            )
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenApiView(views.APIView):
    """
    Вьюсет для получения токена.
    POST-запрос генерирует jwt-token.
    """
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
    """
    Вьюсет для users для администраторов.
    GET-запрос - получение списка пользователей.
    POST-запрос - добавляет нового пользователя.
    GET-запрос по username - получение конкретного пользователя.
    PATCH-запрос по username - изменение данных конкретного пользователя.
    DELETE-запрос по username - удаление конкретного пользователя.
    GET-запрос по me - получение данных своей учетки.
    PATCH=запрос по Me - изменение данных своей учетки.
    """
    queryset = MyUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(detail=False,
            methods=['get', 'patch'],
            url_path=URL_PATH_NAME,
            url_name=URL_PATH_NAME,
            permission_classes=(IsAuthenticated,),
            serializer_class=UserSerializer)
    def users_me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
