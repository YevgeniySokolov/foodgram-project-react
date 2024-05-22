from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
)

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
]
