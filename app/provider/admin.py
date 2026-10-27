from distributions.models import Attribution

from django.contrib import admin

from .models import Provider


class AttributionInline(admin.TabularInline):  # type:ignore[type-arg]
    """Read-only list of the attributions linked to a provider"""

    model = Attribution
    fields = ("attribution_id", "name_en", "description_en")
    readonly_fields = fields
    show_change_link = True
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):  # type:ignore[no-untyped-def]
        return False

    def has_change_permission(self, request, obj=None):  # type:ignore[no-untyped-def]
        return False


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Provider'''

    list_display = ('provider_id', 'acronym_en', 'name_en')
    readonly_fields = ('created', 'updated')
    inlines = [AttributionInline]
