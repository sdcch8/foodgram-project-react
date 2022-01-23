from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, SubscriptionsViewSet, TagViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/', SubscriptionsViewSet.as_view({'get': 'list'}), name='subscriptions-list'),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

    # url(r'^users/$', UserViewSet.as_view({'get': 'list', 'post': 'create'})),
    # url(r'^users/(?P<pk>\d+)/', UserViewSet.as_view({'get': 'retrieve'})),

]
