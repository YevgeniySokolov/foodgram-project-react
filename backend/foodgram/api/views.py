from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponseBadRequest

from recipes.models import Recipe, Tag, Ingredient, ShoppingCart
from foodgram.constants import DOWNLOAD_SHOPPING_CART
from api.filters import RecipeFilter
from api.paginations import LimitPageNumberPagination
from .permissions import UserIsAuthor
from .serializers import (
    ReadShortRecipeSerializer,
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
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    # permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (IsAuthenticated, )
        if self.action == "partial_update":
            self.permission_classes = (UserIsAuthor, )
        return super().get_permissions()

    def create_object(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт не существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ReadShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт был удален ранее.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # @action(detail=True, methods=('POST', 'DELETE'),)
    # def favorite(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.create_connection(
    #             FavoriteRecipe, request.user, pk
    #         )
    #     return self.delete_connection(
    #         FavoriteRecipe, request.user, pk
    #     )

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(IsAuthenticated, ),)
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.create_object(
                ShoppingCart, request.user, pk
            )
        return self.delete_object(
            ShoppingCart, request.user, pk
        )


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
