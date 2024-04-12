from django.urls import path, include
from rest_framework import routers

from api.views import (
    TagViewSet,
    RecipeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    IngredientViewSet,
    DownloadShoppingCartViewSet
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(
    r'recipes/(?P<recipe_pk>\d+)/favorite', FavoriteViewSet,
    basename='favorite'
)
router_v1.register(
    r'recipes/download_shopping_cart',
    DownloadShoppingCartViewSet, basename='download_shopping_cart'
)
router_v1.register(
    r'recipes/(?P<recipe_pk>\d+)/shopping_cart',
    ShoppingCartViewSet, basename='shopping_cart'
)
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
]
