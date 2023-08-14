from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator,
                                    validate_image_file_extension)
from django.db import models

from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(r'^[a-zA-Zа-яА-Я ]+$',
                           'Название рецепта может содержать'
                           'только буквы и пробелы.')
        ]
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
        validators=[validate_image_file_extension, ],
    )
    text = models.TextField(verbose_name='Описание рецепта', )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(300)
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепт'

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if not self.name.isalnum():
            raise ValidationError(
                'Название рецепта должно содержать только буквы и цифры'
            )


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='Название тега',
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет',
    )
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тег'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиент'

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        related_name='amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
    )
    amount = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(20)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient', ],
                name='Unique recipes ingredient.'
            )
        ]
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиента'

    def __str__(self):
        return f'{self.recipe.name}, {self.ingredient.name}: {self.amount}'


class Favorites(models.Model):

    recipe = models.ForeignKey(
        verbose_name="Понравившиеся рецепты",
        related_name="in_favorites",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        related_name="favorites",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is favorite alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Carts(models.Model):

    recipe = models.ForeignKey(
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Владелец списка",
        related_name="carts",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="\n%(app_label)s_%(class)s recipe is cart alredy\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]
