from rest_framework import serializers
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from drf_extra_fields.fields import Base64ImageField
from users.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.password_validation import validate_password


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'color', 'slug',
        ]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'measurement_unit'
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate_amount_of_ingredients(self, amount):
        if amount < 0:
            raise serializers.ValidationError()
        return amount


class RecipeSerializer(serializers.ModelSerializer):
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


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', )
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already exists in your favorites.',
            ),
        )


class CommonRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes'
        ]
        extra_kwargs = {}
        for field in fields:
            extra_kwargs[field] = {'required': True}

    def get_recipes(self, obj):
        recipes_count = self.context.get('recipes_count')
        recipes = obj.recipes.all()[:recipes_count]
        return RecipeSerializer(recipes, many=True).data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True,)
    new_password = serializers.CharField(required=True,)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Wrong old password.'
            )


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


class SubscriptionSerializer(AbstractUserCreateSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = (
            self.context.get('request').query_params.get('recipes_limit')
        )
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return CommonRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author', )
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='You are already subscribed this author.',
            ),
        )

    def validate_author(self, value):
        request = self.context.get('request')
        if request.user == value:
            raise serializers.ValidationError(
                'You are not able to subscribe to yourself.'
            )
        return value
