from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from recipes.models import Recipe


class User(AbstractUser):
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='users',
        blank=True,
        verbose_name='Корзина покупок',
    )
    favorite = models.ManyToManyField(
        'recipes.Recipe',
        blank=True,
        verbose_name='Лист избранного',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author', ],
                name='Unique follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписка'

    def clean(self):
        if self.follower == self.following:
            raise ValidationError('You cannot follow yourself')
        if Follow.objects.filter(
            follower=self.follower, following=self.following
        ).exists():
            raise ValidationError('You are already following this user')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
