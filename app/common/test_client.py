"""This is a workaround to be able to test exception handling with Ninja's TestClient.

The workaround is inspired by the answer to this ticket:
https://github.com/vitalik/django-ninja/issues/1171
"""

from common.exceptions import add_exception_handlers
from ninja import Router
from ninja.testing import TestClient

from django.conf import settings


class BaseNinjaTestCase(object):

    @classmethod
    def setup_client(cls, router: Router):
        settings.DEBUG = True
        settings.IN_TEST = True

        cls.api_client = TestClient(router)
        """
          https://github.com/vitalik/django-ninja/blob/c6d44b62a180fcf8ddfd73d67e0274a77b9d30ae/ninja/testing/client.py#L94-L95
          when we in test we not having urls, so it recreates api instance without attached handlers
        """
        _ = cls.api_client.urls

        add_exception_handlers(cls.api_client.router_or_app.api)
