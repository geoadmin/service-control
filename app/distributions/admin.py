from django.contrib import admin

from .models import Attribution
from .models import Dataset
from .models import PackageDistribution


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Attribution'''

    list_display = ('attribution_id', 'name_en', 'provider')
    list_filter = (('provider', admin.RelatedOnlyFieldListFilter),)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Dataset'''

    list_display = ('dataset_id', 'provider')
    list_filter = (('provider', admin.RelatedOnlyFieldListFilter),)


@admin.register(PackageDistribution)
class PackageDistributionAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Package Distribution'''

    list_display = ('package_distribution_id', 'managed_by_stac', 'dataset')
    list_filter = ('managed_by_stac',)
