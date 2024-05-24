from django.contrib import admin

from .models import (
    Tag, Recipe, Ingredient, ShoppingCart, FavoriteRecipe, IngredientAmount
)
from foodgram.constants import MIN_VALUE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    min_num = MIN_VALUE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('count_in_favorite',)
    inlines = (IngredientAmountInline)
    list_display = (
        'name', 'author', 'image', 'text',
        'cooking_time', 'count_in_favorite'
    )
    list_filter = ('tags', 'author', 'name')

    @admin.display(description='Счетчик в избранном')
    def count_in_favorite(self, recipe):
        return recipe.favoriterecipes.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = list_display


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = list_display
