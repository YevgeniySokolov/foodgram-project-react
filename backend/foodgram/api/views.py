from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (
    Recipe,
    Tag, Ingredient,
    ShoppingCart,
    FavoriteRecipe
)
from foodgram.constants import DOWNLOAD_SHOPPING_CART
from api.filters import RecipeFilter
from api.paginations import LimitPageNumberPagination
from .permissions import UserIsAuthor
from .serializers import (
    ReadShortRecipeSerializer,
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

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (IsAuthenticated, )
        if self.action == "partial_update":
            self.permission_classes = (UserIsAuthor, )
        if self.action == "destroy":
            self.permission_classes = (IsAuthenticated, )
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

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(IsAuthenticated, ),)
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.create_object(
                FavoriteRecipe, request.user, pk
            )
        return self.delete_object(
            FavoriteRecipe, request.user, pk
        )

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

    # @action(detail=False)
    # def download_shopping_cart(self, request):
    #     ingredients = IngredientAmount.objects.filter(
    #         recipe__shoppingcarts__user=request.user
    #     ).values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(amount=Sum('amount')).order_by('ingredient__name')
    #     output = ('Список покупок\n\n')
    #     output += '\n'.join(
    #         [f'{ingredient["ingredient__name"]}'
    #          f' ({ingredient["ingredient__measurement_unit"]})'
    #          f' - {ingredient["amount"]}'
    #          for ingredient in ingredients
    #          ]
    #     )
    #     filename = f'{request.user.username}_shopping_list.txt'
    #     response = HttpResponse(output, content_type='text/plain')
    #     response['Content-Disposition'] = f'attachment; filename={filename}'
    #     return response


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet категорий."""

    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


# class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
#     """ViewSet списка покупок в PDF."""

#     queryset = Recipe.objects.filter(
#         is_in_shopping_cart=True
#     ).all().order_by('name')

#     @action(detail=True,
#             permission_classes=(IsAuthenticated, ),
#             methods=['get'],
#             url_path=DOWNLOAD_SHOPPING_CART)
#     def fetch_report(self, request, *args, **kwargs):
#         short_report = open("PdfFile", 'rb')
#         response = HttpResponse(
#             FileWrapper(short_report),
#             content_type='application/pdf'
#         )
#         return response


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet ингредиента."""

    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    # permission_classes = (IsAuthorizedOrReadOnly, )
