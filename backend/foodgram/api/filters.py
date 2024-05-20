from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='in_cart')

    class Meta:
        model = Recipe
        exclude = ('image',)

    def favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def in_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset
