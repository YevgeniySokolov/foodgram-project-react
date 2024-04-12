import base64

from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import Recipe, Ingredient, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
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

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    ingredients = IngredientSerializer(
        read_only=True,
        many=True
    )
    tag = TagSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tag',
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

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = SlugRelatedField(
        queryset=Ingredient.objects.all(),
        slug_field='slug',
        many=True
    )
    tags = SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tag',
            'image',
            'name',
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
