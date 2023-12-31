import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    """Модель категории произведения."""
    name = models.CharField(
        'Название категории',
        max_length=256
    )
    slug = models.SlugField(
        'Слаг категории',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель жанра произведения."""
    name = models.CharField(
        'Название жанра',
        max_length=256,
        blank=False,
    )
    slug = models.SlugField(
        'Слаг жанра',
        max_length=50,
        unique=True,
        blank=False,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        'Название произведения',
        max_length=256,
        blank=False,
    )
    year = models.IntegerField(
        'Год выпуска',
        blank=False,
    )
    rating = models.IntegerField('Рейтинг произведения')
    description = models.TextField(
        'Описание произведения',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        # on_delete=models.SET_NULL,
        related_name='genre_titles',
        verbose_name='Жанр',
        null=True,
        blank=False,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='category_titles',
        verbose_name='Категория',
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.CheckConstraint(
                check=models.Q(year__lte=dt.datetime.now().year),
                name='check_date'
            ),
        ]

    def clean(self):
        if self.year > dt.datetime.now().year:
            raise ValidationError(
                'Год выпуска произведения не может быть больше текущего года!'
            )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель связи произведения и жанра (многие ко многим)."""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.genre} {self.title}'


class MyUser(AbstractUser):
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'),
        (MODER, 'moderator'),
        (ADMIN, 'admin')
    )
    bio = models.CharField(
        max_length=1024,
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(
        max_length=15,
        verbose_name='Роль',
        choices=ROLE_CHOICES,
        default=USER
    )
    username = models.SlugField(max_length=150, unique=True)

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
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_email_and_username'
            )
        ]
