from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter, RecipesListFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly
from api.serializers import (AddRecipeSerializer, IngredientSerializer,
                             RecipeCrUpdSerializer, RecipeReadSerializer,
                             TagSerializer)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .utils import generate_pdf_shopping_list


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipesListFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCrUpdSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить в избранное."""
        if request.method == 'GET':
            return self.add_obj(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить в список покупок."""
        if request.method == 'GET':
            return self.add_obj(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user
        return generate_pdf_shopping_list(user)

    def add_obj(self, model, user, pk):
        """Добавить рецепт."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = AddRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        """Удалить рецепт."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт не был добавлен или удалён!'
        }, status=status.HTTP_400_BAD_REQUEST)
