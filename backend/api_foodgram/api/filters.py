import django_filters
from rest_framework import filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited', method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart', method='get_is_in_shopping_cart'
    )
    author = django_filters.NumberFilter(
        field_name='author__id'
    )

    def get_is_favorited(self, queryset, name, value):
        if value == 1:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart', 'author')


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
