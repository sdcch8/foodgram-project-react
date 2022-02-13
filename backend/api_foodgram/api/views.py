from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from misc.models import Subscription
from recipes.models import Ingredient, Recipe, Tag

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          SubscriptionSerializer, TagSerializer)
from .utils import download_shopping_cart

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    @action(detail=True, methods=['get', 'post'])
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if (not user.follower.filter(author_id=pk).exists()
                and user.id != int(pk)):
            obj = user.follower.create(author_id=pk)
            obj.save()
            serializer = SubscriptionSerializer(
                author, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        user = request.user
        if user.follower.filter(author_id=pk).exists():
            obj = user.follower.filter(author_id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(
            author__following__user=self.request.user)


class ListRetrieveViewSet(ListAPIView, RetrieveAPIView,
                          viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None
    filter_backends = [IngredientFilter, ]
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    filter_backends = [filters.DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(instance)
        return Response(instance_serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        instance_serializer = RecipeSerializer(instance)
        return Response(instance_serializer.data)

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.AllowAny, ]
        if self.action == 'destroy' or self.action == 'update':
            self.permission_classes = [IsAuthorOrReadOnly, ]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        return download_shopping_cart(self, request)

    def add_recipe(self, model_name, request, pk=None):
        model = apps.get_model('misc', model_name)
        if not model.objects.filter(user_id=request.user.id,
                                    recipe_id=pk).exists():
            obj = model.objects.create(user_id=request.user.id, recipe_id=pk)
            obj.save()
            recipe_serializer = ShortRecipeSerializer(self.get_object())
            return Response(recipe_serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete_recipe(self, model_name, request, pk=None):
        model = apps.get_model('misc', model_name)
        if model.objects.filter(user_id=request.user.id,
                                recipe_id=pk).exists():
            obj = get_object_or_404(model, user=request.user.id, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def favorite(self, request, pk=None):
        return self.add_recipe('Favorite', request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.delete_recipe('Favorite', request, pk)

    @action(detail=True, methods=['get', 'post'])
    def shopping_cart(self, request, pk=None):
        return self.add_recipe('ShoppingCart', request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        return self.delete_recipe('ShoppingCart', request, pk)
