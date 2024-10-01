from django.apps import apps
from django.test.runner import DiscoverRunner


class CustomTestRunner(DiscoverRunner):
    """

    A custom test runner that makes unmanaged models managed prior to tests
    to create the tables.

    See https://dev.to/vergeev/testing-against-unmanaged-models-in-django

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unmanaged_models = []

    def setup_test_environment(self, *args, **kwargs):
        self.unmanaged_models = [
            model for model in apps.get_models()
            if not model._meta.managed
        ]
        for model in self.unmanaged_models:
            model._meta.managed = True
        super().setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super().teardown_test_environment(*args, **kwargs)
        for model in self.unmanaged_models:
            model._meta.managed = False
