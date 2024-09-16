from django.contrib import admin

from .models import Attribution, Dataset


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    '''Admin View for Attribution'''


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    '''Admin View for Dataset'''
