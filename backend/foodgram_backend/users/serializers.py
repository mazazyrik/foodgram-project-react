from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, User


class SimpleRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time', ]


class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'password',
        ]
        extra_kwargs = {}
        for field in fields:
            extra_kwargs[field] = {'required': True}

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if not user.is_authenticated:
    #         return False
    #     follow = user.follower.filter(author=obj)
    #     return follow.exists()

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        password = validated_data.pop('password')
        user: User = super().create(validated_data)
        try:
            user.set_password(password)
            user.save()
            return user
        except serializers.ValidationError as exc:
            user.delete()
            raise exc


class UserWithRecipesSerializer(UserSerializer):
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
        return SimpleRecipeSerializer(recipes, many=True).data


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


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('author', 'follower')
        model = Follow

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['follower', 'author']
            )
        ]

    def validate_author(self, author):
        user = self.context.get('request').user
        if author == user:
            raise serializers.ValidationError(
                'You cannot subscribe on yourself.'
            )
        return author


class CartSerializer(serializers.Serializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )
    attr = serializers.CharField()

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        recipe = attrs.get('recipe')
        attr = attrs.get('attr')
        cart = getattr(user, attr)
        method = request.method
        recipe = attrs.get('recipe')
        if (
            (not cart.filter(id=recipe.id).exists())
            and method == 'DELETE'
        ):
            raise serializers.ValidationError(
                {'errors': 'This recipe is already removed.'}
            )
        elif (
            cart.filter(id=recipe.id).exists()
            and method == 'POST'
        ):
            raise serializers.ValidationError(
                {'errors': 'This recipe is already added.'}
            )
        return super().validate(attrs)

    def destroy(self, recipe):
        user = self.context.get('request').user
        recipe = self.validated_data.get('recipe')
        attr = self.validated_data.get('attr')
        cart = getattr(user, attr)
        cart.remove(recipe)

        return {}

    def create(self, validated_data):
        user = self.context.get('request').user
        recipe = validated_data.get('recipe')
        attr = validated_data.get('attr')
        cart = getattr(user, attr)
        cart.add(recipe)

        return recipe
