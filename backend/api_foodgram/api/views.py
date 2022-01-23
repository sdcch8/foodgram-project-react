from django.db.models import Sum
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from misc.models import Subscription
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, CreateRecipeSerializer,
                          TagSerializer)


class UserViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['get', 'delete'])
    def subscribe(self, request, pk=None):
        user = request.user
        if request.method == 'GET':
            if not user.follower.filter(author_id=pk).exists():
                obj = user.follower.create(author_id=pk)
                obj.save()
                return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
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

    filter_backends = (filters.DjangoFilterBackend, )
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
            self.permission_classes = [IsOwnerOrReadOnly, ]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        )

        ingredients = (ingredients.order_by('ingredient__name')
                                  .values('ingredient__name',
                                          'ingredient__measurement_unit')
                                  .annotate(amount=Sum('amount'))
                       )

        export = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            export.append(f'{name}: {amount} {measurement_unit}\n')

        response = HttpResponse(export, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'

        return response

    @action(detail=True, methods=['get', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'GET':
            if not user.shopping_cart.filter(recipe_id=pk).exists():
                obj = user.shopping_cart.create(recipe_id=pk)
                obj.save()
                return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user.shopping_cart.filter(recipe_id=pk).exists():
                obj = user.shopping_cart.filter(recipe_id=pk)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'delete'])
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'GET':
            if not user.favorite.filter(recipe_id=pk).exists():
                obj = user.favorite.create(recipe_id=pk)
                obj.save()
                return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user.favorite.filter(recipe_id=pk).exists():
                obj = user.favorite.filter(recipe_id=pk)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
