import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer

from users.models import User, Subscription
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    IngredientAmount,
    FavoriteRecipe,
    ShoppingCart
)


class AuthorSerializer(UserSerializer):
    """Сериализатор автора."""

    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, author):
        subscriber = self.context.get('request').user
        if not subscriber.is_authenticated:
            return False
        return Subscription.objects.filter(
            subscriber=subscriber, author=author
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ReadShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов в коротком варианте."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


def check_recipe(self, recipe, checking_model):
    user = self.context['request'].user
    if not user.is_authenticated:
        return False
    return checking_model.objects.filter(
        user=user, recipe=recipe
    ).exists()


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    author = AuthorSerializer(
        read_only=True,
    )
    ingredients = IngredientInRecipeSerializer(
        source='ingredientamounts',
        many=True
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_in_shopping_cart(self, recipe):
        return check_recipe(self, recipe, ShoppingCart)

    def get_is_favorited(self, recipe):
        return check_recipe(self, recipe, FavoriteRecipe)


def create_ingredient(recipe, ingredients):
    for ingredient in ingredients:
        IngredientAmount.objects.create(
            ingredient=ingredient['ingredient'],
            recipe=recipe,
            amount=ingredient['amount']
        )


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""

    image = Base64ImageField(required=True, allow_null=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'обязательное поле.'}
            )
        ingredients_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'повторяющееся поле.'})
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'обязательное поле.'}
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(
                {'ingredients': 'повторяющееся поле.'}
            )
        return super().validate(data)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def update(self, recipe, validated_data):
        tags_ids = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.tags.set(tags_ids)
        create_ingredient(recipe, ingredients)
        return super().update(recipe, validated_data)

    def create(self, validated_data, **kwargs):
        tags_ids = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags_ids)
        create_ingredient(recipe, ingredients)
        return recipe

    def to_representation(self, recipe):
        return ReadRecipeSerializer(recipe, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class BaseWriteFavoriteShoppingCart(serializers.ModelSerializer):
    """Базовый сериализатор для записи избранного рецепта и корзины покупок."""

    def validate(self, data):
        if not Recipe.objects.filter(id=data['recipe'].pk).exists():
            raise serializers.ValidationError('Рецепт не существует.')
        return data

    def to_representation(self, instance):
        return ReadShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data


class WriteFavoriteRecipeSerializer(BaseWriteFavoriteShoppingCart):
    """Сериализатор записи для избранного рецепта."""

    class Meta:
        model = FavoriteRecipe
        fields = ('recipe', 'user')

    def validate(self, data):
        data = super().validate(data)
        if data['user'].favoriterecipes.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data


class WriteShoppingCartRecipeSerializer(BaseWriteFavoriteShoppingCart):
    """Сериализатор для записи корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, data):
        data = super().validate(data)
        if data['user'].shoppingcarts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину покупок.'
            )
        return data
