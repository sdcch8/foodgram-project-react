from django.core.validators import MinValueValidator
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

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}, {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=False
    )
    measurement_unit = models.CharField(
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


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
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}, {self.author}'


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

    class Meta:
        verbose_name = 'Тэги рецепта'
        verbose_name_plural = 'Тэги рецептов'


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

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
