from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientInRecipeCrUpdSerializer(serializers.ModelSerializer):
    """Используется при создании или обновлении рецепта"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Используется для вывода всех полей игредиентов в Response
       при создании/обновлении рецепта и при GET запросе к списку рецептов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeReadSerializer(serializers.ModelSerializer):
    """Используется при запросе списка рецептов (GET)"""
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверка есть ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_cart__user=user,
                                     id=obj.id).exists()


class RecipeCrUpdSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientInRecipeCrUpdSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate(self, data):
        if not data['tags']:
            raise serializers.ValidationError(
                "Необходимо добавить тег!"
            )
        tags = data['tags']
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги должны быть уникальными!')
        data['tags'] = tags

        if not data['ingredients']:
            raise serializers.ValidationError(
                'Не добавлен ингридиент!'
            )
        ingredients = data['ingredients']
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными!'
                )
            ingredient_list.append(ingredient)

            amount = int(ingredient_item['amount'])
            if amount <= 0 or amount > 32767:
                raise serializers.ValidationError(
                    'Введите значение от 0 до 32767'
                )
        data['ingredients'] = ingredients

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0 or int(cooking_time) > 600:
            raise serializers.ValidationError(
                'Укажите время приготовления от 0 до 600 минут'
            )
        data['cooking_time'] = cooking_time
        return data

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        self.add_ingredients(ingredients, recipe)
        tags_data = validated_data.pop('tags')
        recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображает только необходимые поля
       при добавлении в избранное или список покупок."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Избранное."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        write_only_fields = ('user', 'recipe')

    def validate(self, data):
        """Валидация при добавлении рецепта в избранное."""
        if Favorite.objects.filter(user=data['user'],
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже есть в избранном!')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        write_only_fields = ('user', 'recipe')

    def validate(self, data):
        """Валидация при добавлении рецепта в список покупок."""
        if ShoppingCart.objects.filter(user=data['user'],
                                       recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже есть в списке'
                                              ' покупок!')
        return data


class FollowSerializer(serializers.ModelSerializer):
    """Подписки."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return AddRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
