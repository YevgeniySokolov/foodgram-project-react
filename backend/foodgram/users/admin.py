from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')

    list_filter = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
