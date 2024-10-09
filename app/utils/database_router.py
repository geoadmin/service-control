from typing import Any

from django.conf import settings
from django.db.models import Model


class CustomRouter:
    """

    A custom router allowing to additionally read from a BOD.

    """

    def db_for_read(self, model: Model, **hints: Any) -> str | None:
        """ Use BOD for reading BOD models. """

        if model._meta.app_label == 'bod':
            return 'bod'
        return None

    def db_for_write(self, model: Model, **hints: Any) -> str | None:
        """ Use BOD for writing BOD models during tests. """

        if model._meta.app_label == 'bod':
            if not settings.TESTING:
                raise RuntimeError('Writing to the BOD not supported')
            return 'bod'
        return None

    def allow_migrate(
        self, db: Any, app_label: str, model_name: Any = None, **hints: Any
    ) -> bool | None:
        """ Allow BOD migrations only during tests. """

        if app_label == 'bod':
            return settings.TESTING
        return None
