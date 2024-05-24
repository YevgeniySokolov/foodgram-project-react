from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseAdmin):
    readonly_fields = ('subscribers_count', 'recipes_count')
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    ) + readonly_fields
    list_filter = ('email', 'username')

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, user):
        return user.authors.count()

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, user):
        return user.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
