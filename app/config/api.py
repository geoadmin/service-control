from logging import getLogger

from access.api import router as access_router
from distributions.api import router as distributions_router
from ninja import NinjaAPI
from ninja.errors import AuthenticationError
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from provider.api import router as provider_router
from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse

logger = getLogger(__name__)

api = NinjaAPI()

api.add_router("", provider_router)
api.add_router("", distributions_router)
api.add_router("", access_router)


@api.exception_handler(DjangoValidationError)
def handle_django_validation_error(
    request: HttpRequest, exception: DjangoValidationError
) -> HttpResponse:
    """Convert the given validation error  to a response with corresponding status."""
    error_code_unique_constraint_violated = "unique"
    if contains_error_code(exception, error_code_unique_constraint_violated):
        status = 409
    else:
        status = 422

    messages = extract_error_messages(exception)
    return api.create_response(
        request,
        {
            "code": status, "description": messages
        },
        status=status,
    )


@api.exception_handler(Http404)
def handle_404_not_found(request: HttpRequest, exception: Http404) -> HttpResponse:
    return api.create_response(
        request,
        {
            "code": 404, "description": "Resource not found"
        },
        status=404,
    )


@api.exception_handler(Exception)
def handle_exception(request: HttpRequest, exception: Exception) -> HttpResponse:
    logger.exception(exception)
    return api.create_response(
        request,
        {
            "code": 500, "description": "Internal Server Error"
        },
        status=500,
    )


@api.exception_handler(HttpError)
def handle_http_error(request: HttpRequest, exception: HttpError) -> HttpResponse:
    return api.create_response(
        request,
        {
            "code": exception.status_code, "description": exception.message
        },
        status=exception.status_code,
    )


@api.exception_handler(AuthenticationError)
def handle_unauthorized(request: HttpRequest, exception: AuthenticationError) -> HttpResponse:
    logger.exception(exception)
    return api.create_response(
        request,
        {
            "code": 401, "description": "Unauthorized"
        },
        status=401,
    )


@api.exception_handler(NinjaValidationError)
def handle_ninja_validation_error(
    request: HttpRequest, exception: NinjaValidationError
) -> HttpResponse:
    messages: list[str] = []
    for error in exception.errors:
        messages.extend(error.values())
    return api.create_response(
        request,
        {
            "code": 422, "description": messages
        },
        status=422,
    )


root = NinjaAPI(urls_namespace="root")


@root.get("/checker")
def checker(request: HttpRequest) -> dict[str, bool | str]:
    return {"success": True, "message": "OK"}
