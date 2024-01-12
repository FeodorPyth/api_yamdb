from django.core.validators import RegexValidator
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator


from api_yamdb.settings import (
    MAX_LENGTH_SLUG,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME
)

from reviews.models import (
    Category,
    Comment,
    Genre,
    MyUser,
    Review,
    Title,
)

from reviews.validators import (
    validate_username_me,
    validate_year,
)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    slug = serializers.SlugField(
        max_length=MAX_LENGTH_SLUG,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Поле slug должно быть уникальным!'
            )
        ]
    )

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    slug = serializers.SlugField(
        max_length=MAX_LENGTH_SLUG,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Genre.objects.all(),
                message='Поле slug должно быть уникальным!'
            )
        ]
    )

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведения."""
    category = CategorySerializer(
        read_only=True
    )
    genre = GenreSerializer(
        many=True,
        read_only=True
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи произведения."""
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    year = serializers.IntegerField(
        validators=[validate_year]
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'title',
            'text',
            'author',
            'score',
            'pub_date'
        )

    def validate(self, data):
        if self.context['request'].method == 'PATCH':
            return data
        title = self.context['view'].kwargs['title_id']
        author = self.context['request'].user
        if Review.objects.filter(author=author, title__id=title).exists():
            raise serializers.ValidationError(
                'Нельзя повторно комментировать отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        exclude = ('review',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для частичного обновления информации о пользователе."""
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True,
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True,
        validators=[validate_username_me,
                    RegexValidator(
                        regex=r'^[\w.@+-]+\Z',
                        message='Поле username имеет недопустимое значение'
                    )]
    )

    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]
        read_only_fields = ['username', 'email', 'role']


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя админом."""
    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True,
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True,
        validators=[validate_username_me,
                    RegexValidator(
                        regex=r'^[\w.@+-]+\Z',
                        message='Поле username имеет недопустимое значение'
                    )]
    )

    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]

    def validate(self, data):
        try:
            MyUser.objects.get_or_create(
                username=data.get('username'),
                email=data.get('email')
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'Пользователь с таким username/email уже существует'
            )
        return data


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True,
        validators=[validate_username_me,
                    RegexValidator(
                        regex=r'^[\w.@+-]+\Z',
                        message='Поле username имеет недопустимое значение'
                    )]
    )
    confirmation_code = serializers.CharField(max_length=5, required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'confirmation_code')
