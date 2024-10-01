from django.conf import settings


class CustomRouter:
    """

    A custom router allowing to additionally read from a BOD database.

    """

    @property
    def testing(self):
        """ Returns True, if we are currently in a test. """

        return settings.DATABASES['bod']['NAME'] == 'test_bod'

    def db_for_read(self, model, **hints):
        """ Use BOD DB for reading BOD models. """

        if model._meta.app_label == 'bod':
            return 'bod'
        return None

    def db_for_write(self, model, **hints):
        """ Use BOD DB for writing BOD models during tests. """

        if model._meta.app_label == 'bod':
            if not self.testing:
                raise RuntimeError('Writing to the BOD db not supported')
            return 'bod'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """ Allow BOD migrations only during tests. """

        if app_label == 'bod':
            return self.testing
        return None
