from ninja import NinjaAPI
from ninja.errors import AuthenticationError
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from utils.testing import TestClient

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.http import HttpRequest
from django.test import TestCase


class ErrorHandlerTestCase(TestCase):

    def test_handle_404_not_found(self):
        test_api = NinjaAPI(urls_namespace="test-404")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise Http404()

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 404
        assert response.data == {'code': 404, 'description': 'Resource not found'}

    def test_handle_http_error(self):
        test_api = NinjaAPI(urls_namespace="test-http-error")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise HttpError(303, "See other")

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 303
        assert response.data == {'code': 303, 'description': 'See other'}

    def test_handle_ninja_validation_error(self):
        test_api = NinjaAPI(urls_namespace="test-ninja-validation-error")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise NinjaValidationError(errors=[{"email": "Not a valid email."}])

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 422
        assert response.data == {'code': 422, 'description': ['Not a valid email.']}

    def test_handle_unauthorized(self):
        test_api = NinjaAPI(urls_namespace="test-unauthorized")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise AuthenticationError()

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 401
        assert response.data == {'code': 401, 'description': 'Unauthorized'}

    def test_handle_exception(self):
        test_api = NinjaAPI(urls_namespace="test-exception")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise RuntimeError()

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 500
        assert response.data == {'code': 500, 'description': 'Internal Server Error'}

    def test_handle_django_validation_error(self):
        test_api = NinjaAPI(urls_namespace="test-django-validation-error")

        @test_api.get("/trigger")
        def trigger(request: HttpRequest) -> dict[str, bool | str]:
            raise DjangoValidationError(message=[{"email": "Not a valid email."}])

        client = TestClient(test_api)
        response = client.get('/trigger')
        assert response.status_code == 422
        assert response.data == {'code': 422, 'description': ['Not a valid email.']}
