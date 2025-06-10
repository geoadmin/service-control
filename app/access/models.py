from logging import getLogger
from typing import Any
from typing import Iterable

from cognito.utils.client import Client
from utils.fields import CustomSlugField
from utils.short_id import generate_short_id

from django.db import models
from django.db import transaction
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import pgettext_lazy as _

logger = getLogger(__name__)


class CognitoInconsistencyError(Exception):
    """ An exception indicating that the state in the database and state in cognito have
    diverged.
    """


class ActiveUserManager(models.Manager["User"]):
    """ActiveUserManager filters out disabled users."""

    def get_queryset(self) -> models.QuerySet["User"]:
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(models.Model):
    """
    Represents an API user.

    The default queryset (`objects`) excludes disabled users (i.e., those with the `deleted_at`
    attribute set to a valid timestamp). To include disabled users in queries, use `all_objects`.

    This model automatically synchronizes with Cognito during save and delete operations.
    Note: Bulk operations performed via the queryset do not trigger synchronization with Cognito.
    Note: Direct modifications to the `deleted_at` field do not enable/disable the user in Cognito.
    """

    _context = "User model"

    def __str__(self) -> str:
        return str(self.username)

    username = CustomSlugField(_(_context, "User name"), unique=True, max_length=100)
    user_id = models.CharField(_(_context, "User ID"), unique=True, default=generate_short_id)
    created = models.DateTimeField(_(_context, "Created"), auto_now_add=True)
    updated = models.DateTimeField(_(_context, "Updated"), auto_now=True)
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
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:
        """Validates the model before writing it to the database and syncs with cognito."""

        self.full_clean()
        client = Client()
        with transaction.atomic():
            if self._state.adding:
                super().save(force_insert=True, using=using, update_fields=update_fields)
                if not client.create_user(self.user_id, self.username, self.email):
                    logger.critical("User %s already exists in cognito, not created", self.user_id)
                    raise CognitoInconsistencyError()
            else:
                User.all_objects.select_for_update().filter(pk=self.pk).get()
                super().save(force_update=True, using=using, update_fields=update_fields)
                if not client.update_user(self.user_id, self.username, self.email):
                    logger.critical("User %s does not exist in cognito, not updated", self.user_id)
                    raise CognitoInconsistencyError()

    def delete(self,
               using: str | None = None,
               keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Deletes the user from the database and cognito."""

        client = Client()
        with transaction.atomic():
            User.all_objects.select_for_update().filter(pk=self.pk).get()
            result = super().delete(using=using, keep_parents=keep_parents)
            if not client.delete_user(self.user_id):
                logger.critical("User %s does not exist in cognito, not deleted", self.user_id)
                raise CognitoInconsistencyError()
            return result

    def disable(self) -> None:
        """Disables the user in the database and cognito."""

        client = Client()
        with transaction.atomic():
            User.all_objects.select_for_update().filter(pk=self.pk).get()
            # use django.utils.timezone over datetime to use timezone aware objects.
            self.deleted_at = timezone.now()
            super().save(force_update=True)
            if not client.disable_user(self.user_id):
                logger.critical("User %s does not exist in cognito, not disabled", self.user_id)
                raise CognitoInconsistencyError()
