from django.contrib import admin

from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    """Admin View for Provider"""

    list_display = ("provider_id", "acronym_en", "name_en")
    readonly_fields = ("created", "updated")
