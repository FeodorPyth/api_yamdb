from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from api_yamdb.settings import (
    MAX_LENGTH_SLUG,
    MAX_LENGTH_BIO,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_NAME,
    MAX_LENGTH_USERNAME
)
from .validators import validate_username, validate_year


class BaseModel(models.Model):
    """Абстрактная модель. Добавляет имя и слаг с ограничениями по знакам."""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.slug


class Category(BaseModel):
    """Модель категории произведения."""

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    """Модель жанра произведения."""

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(
        'Название произведения',
        max_length=MAX_LENGTH_NAME
    )
    year = models.PositiveIntegerField(
        'Год выпуска',
        validators=[validate_year],
        help_text='Год выпуска должен быть не больше текущего.'
    )
    description = models.TextField(
        'Описание произведения',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='genre_titles',
        verbose_name='Жанр',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True,
    )
    rating = models.IntegerField(
        'Рейтинг',
        null=True
    )

    class Meta:
        ordering = ('year', 'name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель связи произведения и жанра (многие ко многим)."""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles',
    )

    def __str__(self):
        return f'Произведение: {self.title}, Жанр: {self.genre}.'


class MyUser(AbstractUser):
    """Модифицированная модель пользователя."""
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'),
        (MODER, 'moderator'),
        (ADMIN, 'admin')
    )
    bio = models.CharField(
        max_length=MAX_LENGTH_BIO,
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    role = models.CharField(
        max_length=len(max(
            [value for role, value in dict(ROLE_CHOICES).items()], key=len
        )),
        verbose_name='Роль',
        choices=ROLE_CHOICES,
        default=USER
    )
    username = models.SlugField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[validate_username],
        help_text='Имя пользователя не должно быть "me".'
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('role', 'username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_email_and_username'
            )
        ]


class Review(models.Model):
    """Модель отзыва."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Оценка не может быть меньше 1.'),
            MaxValueValidator(10, message='Оценка не может быть больше 10.')
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_title_author'
            ),
        )
        ordering = ('pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.author.username}, оценка: {self.score}.'


class Comment(models.Model):
    """Модель комментария."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:10]
