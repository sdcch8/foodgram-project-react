from django.contrib import admin

from .models import Favorite, ShoppingCart, Subscription


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
