from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Email address',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'First name',
        max_length=150,
    )
    last_name = models.CharField(
        'Last name',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id', 'username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
