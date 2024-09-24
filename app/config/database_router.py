class CustomRouter:
    """
    A router allowing to additionally read from a BOD database.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'bod':
            return 'bod'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'bod':
            return False  # TODO: raise?
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'bod':
            return False
        return None
