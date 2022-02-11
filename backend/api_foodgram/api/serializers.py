import base64
import uuid

from django.core.files.base import ContentFile
from django.forms.fields import ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag_id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)

    image = ImageField()

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'tags',
                  'ingredients',
                  'image',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=obj).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()

    recipes = serializers.SerializerMethodField()

    recipes_count = serializers.ReadOnlyField(source='author.recipe.count')

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(
            author=obj.author)[:int(recipes_limit) or None]
        return ShortRecipeSerializer(queryset, many=True, context=context).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.author.following.filter(user=request.user).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        image_b64 = data
        file_name = str(uuid.uuid4())
        format, imgstr = image_b64.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr),
                           name=file_name + '.' + ext)


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'tags',
                  'ingredients',
                  'image',
                  'name',
                  'text',
                  'cooking_time')

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть >= 1')
        return value

    def create_tags(self, recipe, tags):
        for tag in tags:
            RecipeTag.objects.create(tag_id=tag.id, recipe_id=recipe.id)

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(**ingredient, recipe_id=recipe.id)

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data, author=author)

        self.create_tags(recipe, tags)
        self.create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('tags'):
            RecipeTag.objects.filter(recipe_id=instance.id).delete()
            tags = validated_data.pop('tags')
            self.create_tags(instance, tags)

        if validated_data.get('recipeingredient_set'):
            RecipeIngredient.objects.filter(recipe_id=instance.id).delete()
            ingredients = validated_data.pop('recipeingredient_set')
            self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)
