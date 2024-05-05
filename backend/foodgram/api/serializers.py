import base64
import collections

from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if 'ingredients' not in validated_data:
            if 'tags' not in validated_data:
                instance.save()
                return instance
            else:
                tags_data = validated_data.pop('tags')
                lst = []
                for tag in tags_data:
                    current_tag, status = Tag.objects.get_or_create(
                        **tag
                    )
                    lst.append(current_tag)
                instance.tags.set(lst)

                instance.save()
                return instance

        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)

        if 'tags' not in validated_data:
            instance.save()
            return instance

        tags_data = validated_data.pop('tags')
        lst = []
        for tag in tags_data:
            current_tag, status = Tag.objects.get_or_create(
                **tag
            )
            lst.append(current_tag)
        instance.tags.set(lst)

        instance.save()
        return instance

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
