from rest_framework import serializers
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart
)
from drf_extra_fields.fields import Base64ImageField
from users.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueTogetherValidator


class AbstractUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return request.user.following.filter(author=obj).exists()
        return False


class AbstractUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class TagSerializer(serializers):
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'color', 'slug',
        ]


class IngredientSerializer(serializers):
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'measurement_unit'
        ]


class RecipeIngredientSerializer(serializers):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate_amount_of_ingredients(self, amount):
        if amount < 0:
            raise serializers.ValidationError()
        return amount


class RecipeSerializer(serializers):
    ingredients = RecipeIngredientSerializer(
        many=True,
    )
    tags = TagSerializer(
        many=True,
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
        if value <= 0:
            raise serializers.ValidationError(
                '"cooking_time" must be greater than 0.'
            )
        return value

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagSerializer(instance.tags, many=True).data
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients_set = validated_data.pop('ingredients_set')

        recipe = Recipe.objects.create(author=request.user, **validated_data)

        recipe.tags.set(tags)

        recipe_ingredient_set = []
        for item in ingredients_set:
            ingredient = item.get('ingredient')['id']
            amount = item.get('amount')
            recipe_ingredient_set.append(
                RecipeIngredient(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(
            recipe_ingredient_set, ignore_conflicts=True
        )

        return recipe

    def update(self, instance, validated_data):
        if validated_data:
            instance.name = validated_data.get('name', instance.name)
            instance.image = validated_data.get('image', instance.image)
            instance.text = validated_data.get('text', instance.text)
            instance.cooking_time = validated_data.get(
                'cooking_time', instance.cooking_time
            )

            if 'tags' in validated_data:
                tags = validated_data.pop('tags')
                instance.tags.set(tags)

            if 'ingredients_set' in validated_data:
                ingredients_set = validated_data.pop('ingredients_set')
                instance.ingredients_set.all().delete()
                recipe_ingredient_set = []
                for item in ingredients_set:
                    ingredient = item.get('ingredient')['id']
                    amount = item.get('amount')
                    recipe_ingredient_set.append(
                        RecipeIngredient(
                            recipe=instance, ingredient=ingredient,
                            amount=amount
                        )
                    )
                RecipeIngredient.objects.bulk_create(
                    recipe_ingredient_set, ignore_conflicts=True
                )

            instance.save()
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe', )
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already exists in your shopping cart.',
            ),
        )
