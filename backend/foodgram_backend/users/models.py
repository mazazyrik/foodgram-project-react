from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


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


@receiver(pre_save, sender=Follow)
def check_self_following(sender, instance, **kwargs):
    if instance.follower == instance.user:
        raise ValidationError('You can not follow yourself')
