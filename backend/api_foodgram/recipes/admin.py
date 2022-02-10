from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class TagInLineAdmin(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInLineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'author',
                    'text',
                    'image',
                    'cooking_time',
                    'pub_date',
                    'favorite_count')
    inlines = [TagInLineAdmin, IngredientInLineAdmin]

    def favorite_count(self, obj):
        return obj.favorite.count()


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
