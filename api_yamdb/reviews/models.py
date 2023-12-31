from django.contrib.auth.models import AbstractUser
from django.db import models


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
