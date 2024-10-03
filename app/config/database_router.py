from django.conf import settings


class CustomRouter:
    """

    A custom router allowing to additionally read from a BOD.

    """

    def db_for_read(self, model, **hints):
        """ Use BOD for reading BOD models. """

        if model._meta.app_label == 'bod':
            return 'bod'
        return None

    def db_for_write(self, model, **hints):
        """ Use BOD for writing BOD models during tests. """

        if model._meta.app_label == 'bod':
            if not settings.TESTING:
                raise RuntimeError('Writing to the BOD not supported')
            return 'bod'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """ Allow BOD migrations only during tests. """

        if app_label == 'bod':
            return settings.TESTING
        return None
