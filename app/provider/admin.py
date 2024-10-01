from django.contrib import admin

from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    '''Admin View for Provider'''

    exclude = ('_legacy_id',)
