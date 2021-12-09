from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter

User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipesListFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Показывать рецепты с указанными тегами')
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label='Показывать рецепты выбранного автора')
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='Показывать рецепты, находящиеся в списке избранного')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Показывать рецепты, находящиеся в списке покупок')

    def filter_is_favorited(self, queryset, _name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
