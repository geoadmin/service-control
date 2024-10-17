from typing import Iterable

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import pgettext_lazy as _


class User(models.Model):

    _context = "User model"

    def __str__(self) -> str:
        return str(self.first_name) + str(self.last_name)

    username = models.CharField(_(_context, "User name"), unique=True)
    first_name = models.CharField(_(_context, "First name"))
    last_name = models.CharField(_(_context, "Last name"))
    email = models.EmailField(_(_context, "Email"))

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:
        """Validates the model before writing it to the database."""
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)
