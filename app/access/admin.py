from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from .models import Action
from .models import ResourceType
from .models import Role
from .models import RoleAccess
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for User'''

    list_display = ('user_id', 'username', 'last_name', 'first_name', 'deleted_at', 'provider')
    list_filter = ('deleted_at', ('provider', admin.RelatedOnlyFieldListFilter))
    readonly_fields = ('user_id', 'deleted_at', 'created', 'updated')
    actions = (
        'disable',
        'sync_roles',
    )

    @admin.action(description="Disable selected users")
    def disable(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        for user in queryset:
            user.disable()

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[User]:
        return User.all_objects.get_queryset()

    def delete_queryset(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        for user in queryset:
            user.delete()

    @admin.action(description="Sync roles to cognito")
    def sync_roles(self, request: HttpRequest, queryset: models.QuerySet[User]) -> None:
        """
        Use this as a workaround (at least for now) because cannot do this in user model save()
        because of ManyToMany relationship.
        See https://stackoverflow.com/questions/1925383/issue-with-manytomany-relationships-not-updating-immediately-after-save
        """  # pylint: disable=line-too-long
        for user in queryset:
            user.sync_roles()


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for ResourceType'''

    list_display = ('resource_type_id', 'name')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Action'''


class RoleAccessForm(forms.ModelForm):  # type:ignore[type-arg]
    actions = forms.ModelMultipleChoiceField(queryset=Action.objects.all())

    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and isinstance(instance, RoleAccess):
            self.fields["actions"].help_text = "testvalue"
            self.fields["policyId"].widget.attrs['readonly'] = True


class RoleAccessInline(admin.TabularInline):  # type:ignore[type-arg]
    model = RoleAccess
    extra = 0
    form = RoleAccessForm


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Roles'''

    list_display = ('role_id', 'name')  # data_actions
    inlines = [RoleAccessInline]
