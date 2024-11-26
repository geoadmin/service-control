from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for User'''
    list_display = ('username', 'deleted_at', 'provider')
    list_filter = ('deleted_at', ('provider', admin.RelatedOnlyFieldListFilter))
    actions = ('disable',)

    @admin.action(description="Disable selected users")
    def disable(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        for u in queryset:
            u.disable()

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[User]:
        return User.all_objects.get_queryset()
