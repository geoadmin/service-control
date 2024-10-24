from access.api import router as access_router
from distributions.api import router as distributions_router
from ninja import NinjaAPI
from provider.api import router as provider_router
from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.http import HttpResponse

api = NinjaAPI()

api.add_router("", provider_router)
api.add_router("", distributions_router)
api.add_router("", access_router)


@api.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exception: ValidationError) -> HttpResponse:
    conflict_http_code = 409
    if contains_error_code(exception, conflict_http_code):
        status = conflict_http_code
    else:
        status = 422

    messages = extract_error_messages(exception)
    return api.create_response(
        request,
        {"detail": messages},
        status=status,
    )


root = NinjaAPI(urls_namespace="root")


@root.get("/checker")
def checker(request: HttpRequest) -> dict[str, bool | str]:
    return {"success": True, "message": "OK"}
