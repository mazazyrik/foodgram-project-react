from rest_framework import viewsets
from recipes.models import Tag, Ingredient, Recipe, ShoppingCart
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, ShoppingCartSerializer
from django_filters import rest_framework as filters
from .filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminModeratorOwnerOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.template import loader
from pdfkit import from_string
from rest_framework.decorators import action


class CustomGetViewSet(
    viewsets.ListModelMixin,
    viewsets.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class TagViewSet(CustomGetViewSet):
    queryset = Tag.objects.all
    serializer = TagSerializer


class IngredientViewSet(CustomGetViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = [IsAdminModeratorOwnerOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['GET', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shopping_cart__user=user)
        ingredients = Ingredient.objects.filter(
            recipes_set__recipe__shopping_cart__user=user
        ).annotate(
            total_amount=Sum('recipes_set__amount')
        )
        context = {
            'user': user,
            'recipes': recipes,
            'ingredients': ingredients
        }

        html = loader.render_to_string('shopping_cart.html', context=context)
        output = from_string(html, output_path=False)
        response = HttpResponse(content_type='application/pdf')
        response.write(output)
        return response


class ShoppingCartViewSet(viewsets.CreateModelMixin,
                          viewsets.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    model_class = ShoppingCart

    related_class = Recipe
    related_field = 'recipe'
    related_serializer = RecipeSerializer
