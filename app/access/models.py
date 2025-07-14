from logging import getLogger
from typing import Any
from typing import Iterable

from cognito.utils.client import Client
from utils.fields import CustomSlugField
from utils.short_id import generate_short_id
from verifiedpermissions.utils.client import VPClient

from django.contrib.postgres.fields import ArrayField
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
    roles = models.ManyToManyField("Role")  # type:ignore[var-annotated]

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
                if not client.create_user(
                    self.user_id, self.username, self.email, str(self.provider)
                ):
                    logger.critical("User %s already exists in cognito, not created", self.user_id)
                    raise CognitoInconsistencyError()
            else:
                User.all_objects.select_for_update().filter(pk=self.pk).get()
                super().save(force_update=True, using=using, update_fields=update_fields)
                if not client.update_user(
                    self.user_id, self.username, self.email, str(self.provider)
                ):
                    logger.critical("User %s does not exist in cognito, not updated", self.user_id)
                    raise CognitoInconsistencyError()

    def sync_roles(self) -> None:
        """Sync users roles in cognito. This adds the cognito user to the respective cognito groups.
        """
        client = Client()
        client.remove_all_groups(self.user_id)
        for role in self.roles.all():
            client.add_user_to_group(self.user_id, str(role))

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


class ResourceType(models.Model):
    """ResourceType represents entities that can be accessed or edited by users.

    They map to AVP EntityTypes that are used are resources in policies.
    """

    _context = "ResourceType model"

    def __str__(self) -> str:
        return str(self.resource_type_id)

    resource_type_id = CustomSlugField(
        _(_context, "External ID"), max_length=100, unique=True, db_index=True
    )
    name = models.CharField(_(_context, "Name"))

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:
        """Validates the model before writing it to the database and updating AVP schema."""

        self.full_clean()
        client = VPClient()
        with transaction.atomic():
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields
            )
            client.add_update_resource_type_to_schema(self.resource_type_id)

    def delete(self,
               using: str | None = None,
               keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Deletes from the database and AVP schema."""

        client = VPClient()
        with transaction.atomic():
            client.remove_resource_type_from_schema(self.resource_type_id)
            return super().delete(using=using, keep_parents=keep_parents)


class Action(models.Model):
    """Actions that users can perform on ResourceTypes.

    They map to AVP Actions.
    """

    _context = "Action model"

    def __str__(self) -> str:
        return str(self.action_id)

    action_id = CustomSlugField(
        _(_context, "External ID"),
        max_length=100,
        unique=True,
        db_index=True)
    name = models.CharField(_(_context, "Name"))

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:
        """Validates the model before writing it to the database and syncs with AVP schema."""

        self.full_clean()
        client = VPClient()
        with transaction.atomic():
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields
            )
            client.add_action_to_schema(self.action_id)

    def delete(self,
               using: str | None = None,
               keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Deletes from the database and AVP schema."""

        client = VPClient()
        with transaction.atomic():
            client.remove_action_from_schema(self.action_id)
            return super().delete(using=using, keep_parents=keep_parents)


class Role(models.Model):
    """Role defines Actions per ResourceType that can be performed.

    They map to cognito groups.
    """

    _context = "Role model"

    def __str__(self) -> str:
        return str(self.role_id)

    role_id = CustomSlugField(
        _(_context, "External ID"), max_length=100, unique=True, db_index=True
    )
    name = models.CharField(_(_context, "Name"))

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
                client.create_group(self.role_id)
                super().save(force_insert=True, using=using, update_fields=update_fields)
            else:
                super().save(force_update=True, using=using, update_fields=update_fields)

    def delete(self,
               using: str | None = None,
               keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Deletes the role from the database and the cognito group."""

        client = Client()
        with transaction.atomic():
            client.delete_group(self.role_id)
            User.all_objects.select_for_update().filter(pk=self.pk).get()
            return super().delete(using=using, keep_parents=keep_parents)


class RoleAccess(models.Model):
    """RoleAccess is part of a role and defines which actions can be performed on a specific
    resource type.

    It maps to an AVP policy.
    """

    _context = "RoleDef model"

    role = models.ForeignKey("access.Role", on_delete=models.CASCADE)
    resource_type = models.ForeignKey("access.ResourceType", on_delete=models.CASCADE)
    actions = ArrayField(models.CharField(), default=list)
    policy_id = models.CharField(_(_context, "Policy ID"), null=True, blank=True)

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None
    ) -> None:
        """Validates the model before writing it to the database and creating an AVP policy."""

        self.full_clean()
        client = VPClient()
        with transaction.atomic():
            self.actions = [str(action) for action in self.actions]
            if self.policy_id:
                client.delete_policy(self.policy_id)
            if self._state.adding:
                self.policy_id = client.create_policy(
                    str(self.role), self.actions, str(self.resource_type)
                )
                super().save(force_insert=True, using=using, update_fields=update_fields)
            else:
                self.policy_id = client.create_policy(
                    str(self.role), self.actions, str(self.resource_type)
                )
                super().save(force_update=True, using=using, update_fields=update_fields)
