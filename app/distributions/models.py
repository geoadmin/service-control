from typing import Any
from typing import Iterable

from utils.fields import CustomSlugField

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import pgettext_lazy as _


class Attribution(models.Model):

    _context = "Attribution Model"

    def __str__(self) -> str:
        return str(self.attribution_id)

    attribution_id = CustomSlugField(
        _(_context, "External ID"), max_length=100, unique=True, db_index=True
    )

    name_de = models.CharField(_(_context, "Name (German)"))
    name_fr = models.CharField(_(_context, "Name (French)"))
    name_en = models.CharField(_(_context, "Name (English)"))
    name_it = models.CharField(_(_context, "Name (Italian)"), null=True, blank=True)
    name_rm = models.CharField(_(_context, "Name (Romansh)"), null=True, blank=True)

    description_de = models.CharField(_(_context, "Description (German)"))
    description_fr = models.CharField(_(_context, "Description (French)"))
    description_en = models.CharField(_(_context, "Description (English)"))
    description_it = models.CharField(_(_context, "Description (Italian)"), null=True, blank=True)
    description_rm = models.CharField(_(_context, "Description (Romansh)"), null=True, blank=True)

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)

    _legacy_id = models.IntegerField(
        _(_context, "Legacy ID"),
        null=True,
        blank=True,
        db_index=False,
        help_text="This field is used to track objects imported from the BOD"
    )

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:

        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )


class Dataset(models.Model):

    _context = "Dataset Model"

    def __str__(self) -> str:
        return str(self.dataset_id)


    dataset_id = CustomSlugField(_(_context, "External ID"), unique=True, max_length=100)
    created = models.DateTimeField(_(_context, "Created"), auto_now_add=True)
    updated = models.DateTimeField(_(_context, "Updated"), auto_now=True)

    title_de = models.CharField(_(_context, "Title (German)"))
    title_fr = models.CharField(_(_context, "Title (French)"))
    title_en = models.CharField(_(_context, "Title (English)"))
    title_it = models.CharField(_(_context, "Title (Italian)"), null=True, blank=True)
    title_rm = models.CharField(_(_context, "Title (Romansh)"), null=True, blank=True)
    description_de = models.CharField(_(_context, "Description (German)"))
    description_fr = models.CharField(_(_context, "Description (French)"))
    description_en = models.CharField(_(_context, "Description (English)"))
    description_it = models.CharField(_(_context, "Description (Italian)"), null=True, blank=True)
    description_rm = models.CharField(_(_context, "Description (Romansh)"), null=True, blank=True)

    geocat_id = models.CharField(_(_context, "Geocat ID"), unique=True, max_length=100)
    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)
    attribution = models.ForeignKey(Attribution, on_delete=models.CASCADE)

    _legacy_id = models.IntegerField(
        _(_context, "Legacy ID"),
        null=True,
        blank=True,
        db_index=False,
        help_text="This field is used to track objects imported from the BOD"
    )

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:

        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )


class PackageDistribution(models.Model):

    _context = "Package Distribution Model"

    def __str__(self) -> str:
        return str(self.dataset_id)

    package_distribution_id = CustomSlugField(
        _(_context, "External ID"), unique=True, max_length=100
    )
    managed_by_stac = models.BooleanField(_(_context, "Managed by STAC"))

    _legacy_imported = models.BooleanField(
        _(_context, "Legacy Imported"),
        db_index=False,
        default=False,
        help_text="This field is used to track objects imported from STAC"
    )

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:

        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
