from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters

from recipes.models import Recipe, Tag, Ingredient, User
from foodgram.constants import DOWNLOAD_SHOPPING_CART
from api.filters import RecipeFilter
from .serializers import (
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    IngredientSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet рецептов."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    # filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    # filterset_fields = ('author__id', 'tags__slug')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(
    #         instance,
    #         data=request.data,
    #         partial=True
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet категорий."""

    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


class FavoriteShoppingCartBaseModelViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet избранного рецепта и списка покупок."""

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get("recipe_pk"))

    def get_queryset(self):
        return self.get_recipe()


class FavoriteViewSet(FavoriteShoppingCartBaseModelViewSet):
    """ViewSet избранного рецепта."""

    serializer_class = FavoriteSerializer
    # permission_classes = (IsAuthorizedOrReadOnly, )

    def perform_create(self, serializer):
        recipe = self.get_recipe()
        recipe.is_favorited = True
        serializer.save(recipe=recipe)


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    """ViewSet списка покупок в PDF."""

    queryset = Recipe.objects.filter(
        is_in_shopping_cart=True
    ).all().order_by('name')

    @action(detail=True,
            permission_classes=(IsAuthenticated, ),
            methods=['get'],
            url_path=DOWNLOAD_SHOPPING_CART)
    def fetch_report(self, request, *args, **kwargs):
        short_report = open("PdfFile", 'rb')
        response = HttpResponse(
            FileWrapper(short_report),
            content_type='application/pdf'
        )
        return response


class ShoppingCartViewSet(FavoriteShoppingCartBaseModelViewSet):
    """ViewSet списка покупок."""

    serializer_class = ShoppingCartSerializer
    # permission_classes = (IsAuthorizedOrReadOnly, )

    def perform_create(self, serializer):
        recipe = self.get_recipe()
        recipe.is_in_shopping_cart = True
        serializer.save(recipe=recipe)


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet ингредиента."""

    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    # permission_classes = (IsAuthorizedOrReadOnly, )
