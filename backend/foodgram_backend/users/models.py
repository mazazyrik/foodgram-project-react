from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        blank=False,
        null=False,
    )
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
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
