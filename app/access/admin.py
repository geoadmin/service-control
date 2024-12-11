from django.contrib import admin
from django.db import models
from django.db.models import Model
from django.http import HttpRequest

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for User'''

    list_display = ('user_id', 'username', 'deleted_at', 'provider')
    list_filter = ('deleted_at', ('provider', admin.RelatedOnlyFieldListFilter))
    actions = ('disable',)

    @admin.action(description="Disable selected users")
    def disable(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        for user in queryset:
            user.disable()

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[User]:
        return User.all_objects.get_queryset()

    def delete_queryset(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        for user in queryset:
            user.delete()

    def get_readonly_fields(self, request: HttpRequest, obj: Model | None = None) -> list[str]:
        return ['user_id', 'deleted_at']
