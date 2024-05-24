from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')

    list_filter = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
