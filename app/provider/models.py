from typing import Any
from typing import Iterable

from utils.fields import CustomSlugField

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import pgettext_lazy as _


class Provider(models.Model):
    _context = "Provider model"

    def __str__(self) -> str:
        return str(self.provider_id)

    """
    Note: The "blank=False" for a model field doesn't prevent DB changes.
          It only has an effect on form validation.
    """
    provider_id = CustomSlugField(
        _(_context, "External ID"), max_length=100, unique=True, db_index=True
    )
    created = models.DateTimeField(_(_context, "Created"), auto_now_add=True)
    updated = models.DateTimeField(_(_context, "Updated"), auto_now=True)

    name_de = models.CharField(_(_context, "Name (German)"))
    name_fr = models.CharField(_(_context, "Name (French)"))
    name_en = models.CharField(_(_context, "Name (English)"))
    name_it = models.CharField(_(_context, "Name (Italian)"), null=True, blank=True)
    name_rm = models.CharField(_(_context, "Name (Romansh)"), null=True, blank=True)

    acronym_de = models.CharField(_(_context, "Acronym (German)"))
    acronym_fr = models.CharField(_(_context, "Acronym (French)"))
    acronym_en = models.CharField(_(_context, "Acronym (English)"))
    acronym_it = models.CharField(
        _(_context, "Acronym (Italian)"), null=True, blank=True
    )
    acronym_rm = models.CharField(
        _(_context, "Acronym (Romansh)"), null=True, blank=True
    )

    _legacy_id = models.IntegerField(
        _(_context, "Legacy ID"),
        null=True,
        blank=True,
        db_index=False,
        help_text="This field is used to track objects imported from the BOD",
    )

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
