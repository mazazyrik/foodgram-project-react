from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UsersViewSet, IngredientViewSet,
                       RecipeViewSet, ShoppingCartViewSet,
                       TagViewSet)

router = DefaultRouter()

router.register('users', UsersViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
