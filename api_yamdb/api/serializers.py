import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category,
    Genre,
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
