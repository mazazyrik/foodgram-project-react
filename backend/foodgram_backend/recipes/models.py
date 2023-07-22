from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='tag name',
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='color',
    )
    slug = models.SlugField()

    class Meta:
        verbose_name = 'tag'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='ingredient name',
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='measure units',
    )

    class Meta:
        verbose_name = 'ingridients'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='pub date'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='author'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='name'
    )
    image = models.ImageField(
        upload_to='img/',
        verbose_name='image'
    )
    text = models.TextField(
        verbose_name='description'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time',
        help_text='число минут'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='tag'
    )

    class Meta:
        verbose_name = 'recipe'
        ordering = ('-pub_date', )
        constraints = [
            models.CheckConstraint(
                check=models.Q(cooking_time__gt=0),
                name='rec_cooking_time_gt_0'
            ),
        ]

    def __str__(self):
        return self.name[:40]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredinets_list',
        verbose_name='infgredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        help_text='integer in measurement unit'
    )

    class Meta:
        verbose_name = 'recipe and ingredients'
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='rec_ing_recipe_ingredient_unique'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0), name='rec_ing_amount_gt_0'
            ),
        ]

    def __str__(self):
        return (
            f'Ingredient {self.ingredient_id} in recipe {self.recipe_id}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='shop_user_recipe_unique'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe {self.recipe_id} in {self.user_id} shopping cart'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='fav_user_recipe_unique'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe {self.recipe_id} in {self.user_id} favorites'
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='author'
    )

    class Meta:
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='sub_user_author_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='sub_user_not_equal_author',
            ),
        ]

    def __str__(self):
        return (
            f'User {self.user_id} follows author {self.author_id}'
        )
