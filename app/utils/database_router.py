from typing import Any

from django.conf import settings
from django.db.models import Model


class CustomRouter:
    """

    A custom router allowing to additionally read from a BOD. Ensures that
    tests use the default database.

    """

    def db_for_read(self, model: Model, **hints: Any) -> str | None:
        """ Use BOD for reading BOD models. """

        if settings.TESTING:
            return None

        if model._meta.app_label == 'bod':
            return 'bod'

        return None

    def db_for_write(self, model: Model, **hints: Any) -> str | None:
        """ Use BOD for writing BOD models during tests. """

        if settings.TESTING:
            return None

        if model._meta.app_label == 'bod':
            raise RuntimeError('Writing to the BOD not supported')

        return None

    def allow_migrate(
        self, db: Any, app_label: str, model_name: Any = None, **hints: Any
    ) -> bool | None:
        """ Allow BOD migrations only during tests. """

        if settings.TESTING:
            return None

        if app_label == 'bod':
            return False

        return None
