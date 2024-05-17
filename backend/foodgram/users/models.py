from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import FIELD_EMAIL_LEN, FIELD_NAMES_LEN
from .validators import prohibited_username_validator, regex_validator


class User(AbstractUser):
    """Пользователь."""

    UNAUTH_USER = 'unauth_user'
    AUTH_USER = 'auth_user'
    ADMIN = 'admin'
    CHOICES = [
        (UNAUTH_USER, 'unauth_user'),
        (AUTH_USER, 'auth_user'),
        (ADMIN, 'admin'),
    ]

    username = models.CharField(
        'User Name', unique=True, blank=False, max_length=FIELD_NAMES_LEN,
        validators=[regex_validator, prohibited_username_validator]
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
    role = models.CharField(
        'User Role', choices=CHOICES, default=UNAUTH_USER,
        max_length=FIELD_NAMES_LEN
    )
    is_subscribed = models.BooleanField(
        default=False
    )
    confirmation_code = models.TextField(
        'Confirmation code'
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_auth_user(self):
        return self.role == self.AUTH_USER

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            ),
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписка."""

    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors'
    )
