from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for User'''
