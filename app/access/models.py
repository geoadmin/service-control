from typing import Iterable

from django.db import models
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import pgettext_lazy as _


class ActiveUserManager(models.Manager["User"]):
    """ActiveUserManager filters out any users that have deleted_at set.
    """

    def get_queryset(self) -> models.QuerySet["User"]:
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(models.Model):

    _context = "User model"

    def __str__(self) -> str:
        return str(self.first_name) + str(self.last_name)

    username = models.CharField(_(_context, "User name"), unique=True)
    first_name = models.CharField(_(_context, "First name"))
    last_name = models.CharField(_(_context, "Last name"))
    email = models.EmailField(_(_context, "Email"))
    deleted_at = models.DateTimeField(_(_context, "deleted at"), null=True, blank=True)

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)

    # By default only return active users
    objects = ActiveUserManager()
    all_objects = models.Manager()

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

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

    def disable(self) -> None:
        self.deleted_at = timezone.now()
        self.save()
