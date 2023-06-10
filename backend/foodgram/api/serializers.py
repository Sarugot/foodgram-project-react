from django.core.validators import MinValueValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscribe, User
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from recipes.models import ShoppingСart, Favorite

MIN_VALUE = 0
MAX_VALUE = 32000


class CustomUserCreateSerializer(UserCreateSerializer):
    """Видоизменённый сериализатор создания пользователя djoser."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class CustomUserSerializer(UserSerializer):
    """Видоизменённый сериализатор пользователя djoser."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.followers.filter(
            author=obj.id
        ).exists()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для выведения данных подписок пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.followers.filter(
            author=obj.id
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор создания и удаления новых подписок."""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]

    def to_representation(self, obj):
        return SubscriptionsSerializer(
            obj.author,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError('Невозможно подписаться на себя')
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сокращённый сериализатор рецептов для ответов на часть запросов."""
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)

    def validate(self, obj):
        recipe = self.instance
        user = self.context['request'].user
        if (
            'favorite' in self.context['request'].path
        ) and (
            Favorite.objects.filter(user=user, recipe=recipe).exists()
        ):
            raise exceptions.ValidationError('Рецепт уже добавлен.')
        elif (
            'shopping_cart' in self.context['request'].path
        ) and (
            ShoppingСart.objects.filter(user=user, recipe=recipe).exists()
        ):
            raise exceptions.ValidationError('Рецепт уже добавлен.')
        return obj


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов для тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов для ингридиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связей между рецептом и ингридиентом."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_VALUE), MaxValueValidator(MAX_VALUE)]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientListSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки поля ингридиентов в ответах рецептов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания и удаления избранных рецептов."""
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingСartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления и удаления рецептов в список покупок."""
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data

    class Meta:
        model = ShoppingСart
        fields = ('user', 'recipe')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор GET запросов рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientListSerializer(
        many=True, read_only=True, source='recipeingredient_recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.favorite_users.filter(
            recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.shoppingcart_users.filter(
            recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор POST, DELETE и PATH запросов рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_VALUE), MaxValueValidator(MAX_VALUE)]
    )

    def validate(self, obj):
        if not obj.get('tags'):
            raise serializers.ValidationError('Нужно указать тег.')
        if not obj.get('ingredients'):
            raise serializers.ValidationError('Нужно указать ингредиент.')
        ingredients = [item['id'] for item in obj.get('ingredients')]
        if len(ingredients) > len(set(ingredients)):
            raise serializers.ValidationError('Повторяющиеся ингредиенты.')
        return obj

    def ingredients_create(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.ingredients_create(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.ingredients_create(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time'
                  )
