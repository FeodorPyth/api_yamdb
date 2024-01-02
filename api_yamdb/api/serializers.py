from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category,
    Comment,
    Genre,
    MyUser,
    Review,
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
    rating = serializers.SerializerMethodField()

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

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            average_rating = reviews.aggregate(Avg('score'))['score__avg']
            return round(average_rating, 0)
        else:
            return None


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


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name', read_only=True
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

    # def validate(self, data):
    #     if Review.objects.filter(
    #         author=self.context['request'].user,
    #         title_id=self.context['view'].kwargs.get('title_id')
    #     ).exists() and self.context['request'].method == 'POST':
    #         raise serializers.ValidationError(
    #             'Нельзя оставить два отзыва на одно произведение.')
    #     return data

    # def validate(self, attrs):
    #     title_id = (
    #         self.context['request'].parser_context['kwargs'].get('title_id')
    #     )
    #     title = get_object_or_404(Title, pk=title_id)
    #     user = self.context['request'].user
    #     if (
    #         self.context['request'].method == 'POST'
    #         and Review.objects.filter(author=user, title=title).exists()
    #     ):
    #         raise ValidationError(
    #             'Возможен только один отзыв на произведение.'
    #         )
    #     return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        exclude = ('review',)


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
