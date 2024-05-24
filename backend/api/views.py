from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (
    Recipe,
    Tag, Ingredient,
    ShoppingCart,
    FavoriteRecipe,
    IngredientAmount
)
from api.filters import RecipeFilter, IngredientFilter
from api.paginations import LimitPageNumberPagination
from .permissions import UserIsAuthor
from .serializers import (
    WriteFavoriteRecipeSerializer,
    WriteShoppingCartRecipeSerializer,
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    TagSerializer,
    IngredientSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet рецептов."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (UserIsAuthor, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def create_object(self, serial, request, pk):
        serializer = serial(
            data={'recipe': pk, 'user': request.user.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, model, user, pk):
        get_object_or_404(Recipe, pk=pk)
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт был удален ранее.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=('POST', ),
            permission_classes=(IsAuthenticated, ), )
    def favorite(self, request, pk=None):
        return self.create_object(
            WriteFavoriteRecipeSerializer, request, pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_object(
            FavoriteRecipe, request.user, pk
        )

    @action(detail=True, methods=('POST', ),
            permission_classes=(IsAuthenticated, ),)
    def shopping_cart(self, request, pk=None):
        return self.create_object(
            WriteShoppingCartRecipeSerializer, request, pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_object(
            ShoppingCart, request.user, pk
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        output = ('Список покупок\n\n')
        output += '\n'.join(
            [f'{ingredient["ingredient__name"]}'
             f' ({ingredient["ingredient__measurement_unit"]})'
             f' - {ingredient["amount"]}'
             for ingredient in ingredients
             ]
        )
        filename = 'shopping_list.txt'
        response = HttpResponse(output, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet категорий."""

    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet ингредиента."""

    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
