from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipe',
        null=True
    )
    name = models.CharField(
        max_length=200,
    )
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True
    )
    amount = models.IntegerField()