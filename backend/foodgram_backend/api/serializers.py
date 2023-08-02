from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug', ]


class IngrediendAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def validate_amount(self, amount):
        if amount < 1:
            return serializers.ValidationError({
                'detail': 'Значение должно быть больше 1.'
            })


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', ]


class IngredientsInRecipesPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'amount']

    def validate_amount(self, amount):
        if amount < 0:
            raise serializers.ValidationError(
                {'errors': 'Ingredient amount should be greater than zero.'}
            )
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, )
    ingredients = IngrediendAmountSerializer(
        many=True,
        source='amount',
    )
    author = UserSerializer(read_only=True,)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        ]

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                {'errors': 'Cooking time must be greater than 0.'}
            )

    def get_is_favorited(self, obj: Recipe):
        user: User = self.context.get('request').user
        if user.is_authenticated:
            return user.favorite.filter(id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user: User = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(id=obj.id).exists()
        return False


class RecipeEditCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientsInRecipesPostSerializer(
        many=True,
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time'
        ]

    @staticmethod
    def create_ingredients(ingredients, recipe: Recipe):
        ingredients_amount = [IngredientAmount(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientAmount.objects.bulk_create(ingredients_amount)

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными!'
                })
            ingredients_set.add(ingredient_id)

        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredient = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredient, recipe)
        return recipe

    def update(self, instance: Recipe, validated_data):
        if 'tags' in self.validated_data:
            tags = validated_data.pop('tags', instance.tags.all())
            instance.tags.set(tags)

        if 'ingredients' in self.validated_data:
            ingredients = validated_data.pop('ingredients')
            IngredientAmount.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        super().update(instance, validated_data)

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance, context=context
        ).data

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            return serializers.ValidationError({
                'detail': 'Время готовки не можеть меньше 0'
            })
        return cooking_time
