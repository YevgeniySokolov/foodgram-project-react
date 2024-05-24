from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer

from .models import Subscription
from api.serializers import ReadShortRecipeSerializer, ReadRecipeSerializer

User = get_user_model()


class FoodgramUserSerializer(UserSerializer):

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
