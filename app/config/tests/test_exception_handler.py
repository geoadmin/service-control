from botocore.exceptions import EndpointConnectionError
from config.api import api
from ninja import Router
from ninja.errors import AuthenticationError
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.http import HttpRequest
from django.test import TestCase

router = Router()
api.add_router("", router)


@router.get("trigger-not-found")
def trigger_not_found(request: HttpRequest) -> dict[str, bool | str]:
    raise Http404()


@router.get("trigger-does-not-exist")
def trigger_does_not_exist(request: HttpRequest) -> dict[str, bool | str]:
    get_user_model().objects.get()


@router.get("trigger-http-error")
def trigger_http_error(request: HttpRequest) -> dict[str, bool | str]:
    raise HttpError(303, "See other")


@router.get("/trigger-ninja-validation-error")
def trigger_ninja_validation_error(request: HttpRequest) -> dict[str, bool | str]:
    raise NinjaValidationError(errors=[{"email": "Not a valid email."}])


@router.get("/trigger-authentication-error")
def trigger_authentication_error(request: HttpRequest) -> dict[str, bool | str]:
    raise AuthenticationError()


@router.get("/trigger-internal-server-error")
def trigger_internal_server_error(request: HttpRequest) -> dict[str, bool | str]:
    raise RuntimeError()


@router.get("/trigger-django-validation-error")
def trigger_django_validation_error(request: HttpRequest) -> dict[str, bool | str]:
    raise DjangoValidationError(message=[{"email": "Not a valid email."}])


@router.get("/trigger-cognito-connection-error")
def trigger_cognito_connection_error(request: HttpRequest) -> dict[str, bool | str]:
    raise EndpointConnectionError(endpoint_url='localhost')


class ErrorHandlerTestCase(TestCase):

    def test_handle_404_not_found(self):
        response = self.client.get('/api/trigger-not-found')
        assert response.status_code == 404
        assert response.json() == {'code': 404, 'description': 'Resource not found'}

    def test_handle_does_not_exist(self):
        response = self.client.get('/api/trigger-does-not-exist')
        assert response.status_code == 404
        assert response.json() == {'code': 404, 'description': 'Resource not found'}

    def test_handle_http_error(self):
        response = self.client.get('/api/trigger-http-error')
        assert response.status_code == 303
        assert response.json() == {'code': 303, 'description': 'See other'}

    def test_handle_ninja_validation_error(self):
        response = self.client.get('/api/trigger-ninja-validation-error')
        assert response.status_code == 422
        assert response.json() == {'code': 422, 'description': ['Not a valid email.']}

    def test_handle_unauthorized(self):
        response = self.client.get('/api/trigger-authentication-error')
        assert response.status_code == 401
        assert response.json() == {'code': 401, 'description': 'Unauthorized'}

    def test_handle_exception(self):
        response = self.client.get('/api/trigger-internal-server-error')
        assert response.status_code == 500
        assert response.json() == {'code': 500, 'description': 'Internal Server Error'}

    def test_handle_django_validation_error(self):
        response = self.client.get('/api/trigger-django-validation-error')
        assert response.status_code == 422
        assert response.json() == {'code': 422, 'description': ['Not a valid email.']}

    def test_handle_cognito_connection_error(self):
        response = self.client.get('/api/trigger-cognito-connection-error')
        assert response.status_code == 503
        assert response.json() == {'code': 503, 'description': 'Service Unavailable'}
