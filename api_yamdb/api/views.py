import random

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import AUTHENTICATION_EMAIL
from .filters import TitleViewSetFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminPermission,
    IsAuthorOrModerOrAdmin
)
from reviews.models import (
    Category,
    Genre,
    Comment,
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
from .viewsets import BaseCategoryGenreViewset


class CategoryViewSet(BaseCategoryGenreViewset):
    """Вьюсет для категорий.
    
    Доступные запросы:
    GET-запрос - получение списка категорий;
    POST-запрос - добавляет новую категорию;
    DELETE-запрос - удаление категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewset):
    """Вьюсет для жанров.
    
    Доступные запросы:
    GET-запрос - получение списка жанров;
    POST-запрос - добавляет новый жанр;
    DELETE-запрос - удаление жанра.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений.
    
    Доступные запросы:
    GET-запрос - получение списка произведений,
    по id получение конкретного произведения;
    POST-запрос - добавляет новое произведение;
    PATCH-запрос - частичное обновление произведения;
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
    """Вьюсет для отзывов.

    Доступные запросы:
    GET-запрос - получение списка отзывов,
    по id получение конкретного отзыва;
    POST-запрос - добавляет новый отзыв;
    PATCH-запрос - частичное обновление отзыва;
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

    def perform_update(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review_id = self.kwargs.get('pk')
        author = Review.objects.get(pk=review_id).author
        serializer.save(author=author, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев.
    
    Доступные запросы:
    GET-запрос - получение списка комментариев,
    по id получение конкретного комментария;
    POST-запрос - добавляет новый комментарий;
    PATCH-запрос - частичное обновление комментария;
    DELETE-запрос - удаление комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerOrAdmin,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        comment_id = self.kwargs.get('pk')
        author = Comment.objects.get(pk=comment_id).author
        serializer.save(author=author, review=review)


class SignUpAPIView(views.APIView):
    """Вьюсет для получения кода подтверждения.
    
    Доступные запросы:
    POST-запрос с полями username, email
    генерирует email с confirmation_code.
    """
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


class TokenApiView(views.APIView):
    """Вьюсет для получения токена.
    
    Доступные запросы:
    POST-запрос с полями username, confirmation_code
    генерирует jwt-token.
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
    """Вьюсет для users для администраторов.
    
    Доступные запросы:
    GET-запрос - получение списка пользователей;
    POST-запрос - добавляет нового пользователя;
    GET, PATCH, DELETE-запрос - получение,
    частичное изменение, удаление пользователя по его username.
    """
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
