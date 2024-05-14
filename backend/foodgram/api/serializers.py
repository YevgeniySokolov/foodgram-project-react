import base64
import collections

from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from users.models import User
from recipes.models import Recipe, Ingredient, Tag, IngredientAmount


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор автора."""

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
        # validators=[UniqueValidator(queryset=Ingredient.objects.all())]
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


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""

    image = Base64ImageField(required=True, allow_null=True)
    ingredients = IngredientInRecipeSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    def validate(self, data):
        errors = []
        ingredients_ids = []
        if not data['ingredients']:
            errors.append('Ingredients обязательное поле.')
        # UniqueValidator(queryset=Ingredient.objects.all())
        for ingredient in data['ingredients']:
            ingredients_ids.append(ingredient['id'])
        if len(ingredients_ids) != len(set(ingredients_ids)):
            errors.append('Повторяющееся поле ingredient.')
        if not data['tags']:
            errors.append('Tags обязательное поле.')
        if len(data['tags']) != len(set(data['tags'])):
            errors.append('Повторяющееся поле ingredient.')
        if errors:
            raise serializers.ValidationError(errors)
        return data

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
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=IngredientAmount.objects.all(),
        #         recipe=Recipe.objects.get(),
        #         fields=['recipe', 'ingredients']
        #     )
        # ]
        # validators = [
        #     UniqueValidator(
        #         queryset=Ingredient.objects.all()
        #     )
        # ]

    def update(self, recipe, validated_data):
        tags_ids = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.tags.set(tags_ids)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'])
        return super().update(recipe, validated_data)

    def create(self, validated_data, **kwargs):
        tags_ids = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags_ids)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'])
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
    """Сериализатор для избранного рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
