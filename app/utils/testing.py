from botocore.exceptions import EndpointConnectionError
from config.api import handle_404_not_found
from config.api import handle_cognito_connection_error
from config.api import handle_django_validation_error
from config.api import handle_exception
from config.api import handle_http_error
from config.api import handle_ninja_validation_error
from config.api import handle_unauthorized
from ninja import NinjaAPI
from ninja import Router
from ninja.errors import AuthenticationError
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from ninja.testing import TestClient as BaseTestClient

from django.core.exceptions import ValidationError
from django.http import Http404


class TestClient(BaseTestClient):
    """ A patched version of the ninja test client which re-attaches the custom exception handlers.
    This allows using the custom exception handling in tests.

    """

    def __init__(
        self,
        router_or_app: NinjaAPI | Router,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(router_or_app=router_or_app, headers=headers)

        # In order to be able to test exception handling, we need to attach the
        # exception handlers ourselves. To that end, first trigger a recreation
        # of the api instance on the TestClient by calling the urls property.
        # Then attach the exception handlers manually.
        #
        # Inspired from this GitHub discussion on django-ninja:
        # https://github.com/vitalik/django-ninja/discussions/1211
        _ = self.urls
        api: NinjaAPI
        if isinstance(self.router_or_app, NinjaAPI):
            api = self.router_or_app
        else:
            assert self.router_or_app.api
            api = self.router_or_app.api
        for exception, handler in (
            (Http404, handle_404_not_found),
            (HttpError, handle_http_error),
            (NinjaValidationError, handle_ninja_validation_error),
            (ValidationError, handle_django_validation_error),
            (AuthenticationError, handle_unauthorized),
            (Exception, handle_exception),
            (EndpointConnectionError, handle_cognito_connection_error)
        ):
            # ignore that add_exception_handler expects the handler to also accept type[ExceptionXY]
            # as this is documented otherwise in the ninja docs
            api.add_exception_handler(exception, handler)  # type:ignore[arg-type]
