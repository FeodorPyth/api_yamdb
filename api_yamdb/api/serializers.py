from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    Category,
    Genre,
    MyUser,
    Title,
)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    slug = serializers.RegexField(
        max_length=50,
        required=True,
        regex=r'^[-a-zA-Z0-9_]+$',
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Поле slug должно быть уникальным!'
            )
        ]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    slug = serializers.RegexField(
        max_length=50,
        required=True,
        regex=r'^[-a-zA-Z0-9_]+$',
        validators=[
            UniqueValidator(
                queryset=Genre.objects.all(),
                message='Поле slug должно быть уникальным!'
            )
        ]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


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
        source='reviews__score__avg', read_only=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для частичного обновления информации о пользователе."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
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
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
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

    def validate_username(self, value):
        if 'me' == value:
            raise serializers.ValidationError(
                {'username': 'Имя "me" для пользователя запрещено!'}
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
    )
    confirmation_code = serializers.CharField(max_length=5, required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'confirmation_code')
