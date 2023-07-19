from rest_framework import viewsets
from recipes.models import Tag, Ingredient, Recipe, ShoppingCart
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    AbstractUserSerializer,
    ChangePasswordSerializer,
    AuthorSerializer,
    SubscribeSerializer
)
from django_filters import rest_framework as filters
from .filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminModeratorOwnerOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.template import loader
from pdfkit import from_string
from rest_framework.decorators import action
from users.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import mixins


class CustomGetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class UsersViewSet(CustomGetViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = AbstractUserSerializer
    permission_classes = [AllowAny, ]

    @action(
        detail=False,
        methods=[
            'get',
        ],
        permission_classes=[IsAuthenticated, ],
        url_path='me',
    )
    def get_me(self, request):
        data = AbstractUserSerializer(
            request.user,
            context={
                'request': request
            }
        ).data
        return Response(
            data, status=200
        )

    @action(
        detail=False,
        methods=[
            'POST',
        ],
        permission_classes=[IsAuthenticated, ],
        url_path='set_password',
    )
    def set_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=204)

    @action(
        detail=True,
        methods=['POST', ],
        permission_classes=[IsAuthenticated, ],
        url_path='subscribe',
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        data = {
            'author': pk,
            'follower': request.user.id,
        }
        serializer = SubscribeSerializer(
            data=data, context={'request': request, }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipes_limit = self.request.query_params.get('recipes_limit', 99999)

        return Response(
            AuthorSerializer(
                author, context={
                    'request': request,
                    'recipes_limit': recipes_limit
                }
            ).data
        )

    @action(
        detail=False,
        methods=['GET', ],
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        follows = request.user.follows.all()
        ids = follows.values_list('author_id', flat=True)
        queryset = User.objects.filter(id__in=ids)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AuthorSerializer(
                page, many=True, context={
                    'request': request
                }
            )
            return self.get_paginated_response(serializer.data)

        serializer = AuthorSerializer(
            queryset, many=True, context={
                'request': request
            }
        )

        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


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


class ShoppingCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    model_class = ShoppingCart

    related_class = Recipe
    related_field = 'recipe'
    related_serializer = RecipeSerializer
