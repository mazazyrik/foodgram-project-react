from django.core.validators import validate_image_file_extension
from django.db import models

# from users.models import User
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='название тега',
    )
    color = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='цвет'
    )
    slug = models.SlugField()

    class Meta:
        verbose_name = 'тег'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='единицы измерения',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиент'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='дата публикации'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='имя'
    )
    image = models.ImageField(
        upload_to='img/',
        verbose_name='картинка'
    )
    text = models.TextField(
        verbose_name='описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время готовки',
        help_text='число минут'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='теги'
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
        related_name='рецпет',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='список ингреденетов',
        verbose_name='ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        help_text='integer in measurement unit'
    )

    class Meta:
        verbose_name = 'рецепт и ингредиенты'
        verbose_name_plural = 'рецепт и ингредиенты'
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(
                fields=['рецепт', 'ingredient'],
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
