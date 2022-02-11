from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionsViewSet,
                    TagViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'}),
         name='subscriptions-list'),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
