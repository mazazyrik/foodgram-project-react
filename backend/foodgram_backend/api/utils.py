# flake8: noqa

from django.db.models import Sum

from recipes.models import IngredientAmount
from users.models import User


def make_cart_file(user: User):

    ingredients = IngredientAmount.objects.filter(
        recipe__in=user.shopping_cart.all()
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).order_by('ingredient__name').annotate(
        ingr_amount=Sum('amount')
    )
    return ingredients
