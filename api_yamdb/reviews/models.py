import datetime as dt

from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    """Модель категории произведения"""
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
    """Модель жанра произведения"""
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
    """Модель произведения"""

    name = models.TextField(
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
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Жанр',
        blank=False,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        blank=False,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.CheckConstraint(
                check=models.Q(year__lte=dt.datetime.now().year),
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
    """Модель связи произведения и жанра (многие ко многим)"""
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
