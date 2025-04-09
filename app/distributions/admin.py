from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

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

    list_display = ('dataset_id', 'title_en', 'provider')
    list_filter = (('provider', admin.RelatedOnlyFieldListFilter),)

    def get_form(
        self,
        request: HttpRequest,
        obj: Dataset | None = None,
        change: bool = False,
        **kwargs: Any
    ) -> Any:
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        self.add_geocat_url_help_text(form, obj)
        return form

    def add_geocat_url_help_text(self, form: Any, obj: Dataset | None = None) -> None:
        if not obj:
            return
        form.base_fields["geocat_id"].help_text = format_html(
            "<a href='{url}'>{url}</a>",
            url=f"https://www.geocat.ch/datahub/dataset/{obj.geocat_id}",
        )


@admin.register(PackageDistribution)
class PackageDistributionAdmin(admin.ModelAdmin):  # type:ignore[type-arg]
    '''Admin View for Package Distribution'''

    list_display = ('package_distribution_id', 'managed_by_stac', 'dataset')
    list_filter = ('managed_by_stac',)
