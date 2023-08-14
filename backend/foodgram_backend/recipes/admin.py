from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'pub_date']
    search_fields = ['name', 'author']
    list_filter = ['author', 'name', 'tags']

    def number_of_additions(self, obj: Recipe):
        return obj.shopping_users.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]
    search_fields = ['name', 'measure_unit']
    list_filter = ['name', ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ['name', 'colow', 'slug']
    list_filter = ['name', 'color', 'slug']
