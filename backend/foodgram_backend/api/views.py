from urllib.parse import unquote

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .pagination import CustomPagination
from .serializers import (IngredientSerializer, RecipeEditCreateSerializer,
                          RecipeSerializer, TagSerializer)
from .utils import make_cart_file
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import mixins
from rest_framework.permissions import AllowAny


class CustomGetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class TagViewSet(CustomGetViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(CustomGetViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')

        if name:
            if name[0] == '%':
                name = unquote(name)
            name = name.lower()
        return list(queryset.filter(name__istartswith=name))


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny, ]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeEditCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        # Only for auth users
        if not self.request.user.is_authenticated:
            return queryset

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart:
            ids = self.request.user.shopping_cart.values_list('id', flat=True)
            queryset = queryset.filter(id__in=ids)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            ids = self.request.user.favorite.values_list('id', flat=True)
            queryset = queryset.filter(id__in=ids)

        return queryset

    @action(detail=True, methods=['POST', ], url_path='shopping_cart',)
    def shopping_cart(self, request, pk=None):
        return Cart(pk, request, 'shopping_cart').add()

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        return Cart(pk, request, 'shopping_cart').remove()

    @action(detail=True, methods=['POST', ], url_path='favorite', )
    def favorite(self, request, pk=None):
        return Cart(pk, request, 'favorite').add()

    @favorite.mapping.delete
    def remove_favorite_list(self, request, pk=None):
        return Cart(pk, request, 'favorite').remove()

    @action(
        detail=False,
        methods=['GET', ],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        result = make_cart_file(request.user)
        file_name = f'{request.user}_shopping_list.txt'
        lines = []
        for data in result:
            name = data.get('ingredient__name')
            measurement_unit = data.get('ingredient__measurement_unit')
            amount = data.get('ingr_amount')
            lines.append(f'{name}: {amount} {measurement_unit}')

        response_content = '\n'.join(lines)
        response = Response(
            response_content, content_type="text/plain, charset=utf8"
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
