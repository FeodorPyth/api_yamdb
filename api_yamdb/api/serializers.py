import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category,
    Genre,
    MyUser,
    Title,
)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для Жанра."""
    name = serializers.CharField(max_length=256)
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
        fields = (
            'name',
            'slug',
        )
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для Произведения."""
    category = SlugRelatedField(
        slug_field='slug',
        read_only=True
    )
    genre = GenreSerializer(
        many=True,
        read_only=True
    )
    name = serializers.CharField(max_length=256)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        model = Title

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                {'year': 'Год выпуска произведения не может быть в будущем!'}


class UserSerializer(serializers.ModelSerializer):
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


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для Категории."""
    name = serializers.CharField(max_length=256)
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
        fields = (
            'name',
            'slug',
        )
        model = Category


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
    )
    confirmation_code = serializers.CharField(max_length=5, required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'confirmation_code')
