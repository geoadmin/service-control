from access.api import router as access_router
from distributions.api import router as distributions_router
from ninja import NinjaAPI
from provider.api import router as provider_router
from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse

api = NinjaAPI()

api.add_router("", provider_router)
api.add_router("", distributions_router)
api.add_router("", access_router)


@api.exception_handler(ValidationError)
def validation_error_to_response(request: HttpRequest, exception: ValidationError) -> HttpResponse:
    """Convert the given validation error  to a response with corresponding status."""
    error_code_unique_constraint_violated = "unique"
    if contains_error_code(exception, error_code_unique_constraint_violated):
        status = 409
    else:
        status = 422

    messages = extract_error_messages(exception)
    return api.create_response(
        request,
        {"detail": messages},
        status=status,
    )


@api.exception_handler(Http404)
def http404_to_response(request: HttpRequest, exception: Http404) -> HttpResponse:
    """Convert the given exception to a Not Found response with the actual exception message.

    Without this, we would only see "Not found" in the response even if the
    original exception message is more detailed like "No User matches the given query.".
    """
    return api.create_response(
        request,
        {"detail": str(exception)},
        status=404,
    )


@api.exception_handler(Exception)
def exception_to_response(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Convert the given exception to a generic internal server error."""
    return api.create_response(
        request,
        {"detail": str(exception)},
        status=500,
    )


root = NinjaAPI(urls_namespace="root")


@root.get("/checker")
def checker(request: HttpRequest) -> dict[str, bool | str]:
    return {"success": True, "message": "OK"}
