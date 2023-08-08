from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('id', 'username', 'first_name', 'last_name', 'email', )
    search_fields = ('username', 'email', )
    list_filter = ('first_name', 'email', )
    list_display_links = ('username', )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ('follower', 'author')
    list_filter = ('follower', 'author')
    search_fields = ('follower', 'author')
