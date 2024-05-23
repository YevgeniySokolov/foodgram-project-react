from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import truncatechars

from foodgram.constants import (
    FIELD_EMAIL_LEN,
    FIELD_NAMES_LEN,
    DEFAULT_TRUNCATE
)
from .validators import prohibited_username_validator, regex_validator


class User(AbstractUser):
    """Пользователь."""

    username = models.CharField(
        'User Name', unique=True, blank=False, max_length=FIELD_NAMES_LEN,
        validators=[regex_validator, prohibited_username_validator]
    )
    password = models.CharField(
        max_length=FIELD_NAMES_LEN,
    )
    email = models.EmailField(
        'E-mail address', unique=True, blank=False, max_length=FIELD_EMAIL_LEN
    )
    first_name = models.CharField(
        'First Name', blank=True, max_length=FIELD_NAMES_LEN
    )
    last_name = models.CharField(
        'Last Name', blank=True, max_length=FIELD_NAMES_LEN
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            ),
        ]

    def __str__(self):
        return truncatechars(self.username, DEFAULT_TRUNCATE)


class Subscription(models.Model):
    """Подписка."""

    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'
