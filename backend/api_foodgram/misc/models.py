from django.db import models

from recipes.models import Recipe
from users.models import User


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='Favorite unique constraint'
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='Subscription unique constraint'
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
