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

router = Router()
api.add_router("", router)


@router.get("trigger-not-found")
def trigger_not_found(request: HttpRequest) -> dict[str, bool | str]:
    raise Http404()


@router.post("trigger-not-found-post")
def trigger_not_found_post(request: HttpRequest) -> dict[str, bool | str]:
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


@router.get("/trigger-200-response")
def trigger_200_response(request: HttpRequest) -> dict[str, bool | str]:
    return "Hello World"
