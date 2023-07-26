from django.contrib import admin

from .models import Ingredient, IngredientAmount, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'tags__name', 'author__username', )


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )


class IngredientAmountAdmin(admin.ModelAdmin):
    pass


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
