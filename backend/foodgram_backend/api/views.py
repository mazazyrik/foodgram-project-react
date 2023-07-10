from rest_framework import viewsets
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import TagSerializer


class CustomGetViewSet(
    viewsets.ListModelMixin,
    viewsets.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class TagViewSet(viewsets):
    queryset = Tag.objects.all
    serializer = TagSerializer
