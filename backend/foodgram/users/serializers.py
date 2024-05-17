from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import Subscription
from .validators import prohibited_username_validator, regex_validator
from foodgram.constants import FIELD_NAMES_LEN, FIELD_EMAIL_LEN
from api.serializers import ReadShortRecipeSerializer, ReadRecipeSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    email = serializers.EmailField(
        required=True, max_length=FIELD_EMAIL_LEN
    )
    username = serializers.CharField(
        validators=[
            regex_validator, prohibited_username_validator,
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True, max_length=FIELD_NAMES_LEN
    )
    first_name = serializers.CharField(
        required=True, max_length=FIELD_NAMES_LEN
    )
    last_name = serializers.CharField(
        required=True, max_length=FIELD_NAMES_LEN
    )
    password = serializers.CharField(
        required=True, max_length=FIELD_NAMES_LEN,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):

    email = serializers.EmailField(
        max_length=FIELD_EMAIL_LEN
    )
    username = serializers.CharField(
        validators=[
            regex_validator, prohibited_username_validator,
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True, max_length=FIELD_NAMES_LEN
    )
    first_name = serializers.CharField(
        max_length=FIELD_NAMES_LEN
    )
    last_name = serializers.CharField(
        max_length=FIELD_NAMES_LEN
    )
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        subscriber = self.context['request'].user
        if Subscription.objects.filter(subscriber=subscriber,
                                       author=obj).exists():
            return True
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор списка подписок."""

    recipes = ReadRecipeSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['subscriber', 'author']
            )
        ]

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ReadShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, author):
        subscriber = self.context.get('request').user
        return Subscription.objects.filter(
            subscriber=subscriber, author=author
        ).exists()

    # def validate_author(self, value):
    #     if not value:
    #         raise serializers.ValidationError(
    #             'Заполните обязательное поле "author".')
    #     if value == self.context["request"].user:
    #         raise serializers.ValidationError(
    #             'Нет возможности подписаться на самого себя.')
    #     return value


# class MeUserSerializer(serializers.ModelSerializer):
#
#    is_subscribed = serializers.SerializerMethodField()
#
#    class Meta:
#        model = User
#        fields = (
#            'email',
#            'id',
#            'username',
#            'first_name',
#            'last_name',
#            'is_subscribed',
#        )
#
#    def get_is_subscribed(self, obj):
#        return False


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля."""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User


# class GetProfileSerializer(CustomUserSerializer):
#    """Сериализатор профиля пользователя."""
