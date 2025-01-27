import sys
from logging import getLogger
from typing import Any
from typing import List
from typing import Optional
from typing import TypedDict

from access.api import router as access_router
from botocore.exceptions import EndpointConnectionError
from distributions.api import router as distributions_router
from ninja import NinjaAPI
from ninja.errors import AuthenticationError
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from provider.api import router as provider_router
from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse

logger = getLogger(__name__)

LogExtra = TypedDict(
    'LogExtra',
    {
        'http': {
            'request': {
                'method': str, 'header': dict[str, str]
            },
            'response': {
                'status_code': int, 'header': dict[str, str]
            }
        },
        'url': {
            'path': str, 'scheme': str
        }
    }
)


def generate_log_extra(request: HttpRequest, response: HttpResponse) -> LogExtra:
    """Generate the extra dict for the logging calls

    This will format the following extra fields to be sent to the logger:

    request:
        http:
            request:
                method: GET | POST | PUT | ...
                header: LIST OF HEADERS
            response:
                header: LIST OF HEADERS
                status_code: STATUS_CODE

    url:
        path: REQUEST_PATH
        scheme: REQUEST_SCHEME

    Args:
        request (HttpRequest): Request object
        response (HttpResponse): Response object

    Returns:
        dict: dict of extras
    """
    return {
        'http': {
            'request': {
                'method': request.method or 'UNKNOWN',
                'header': {
                    k.lower(): v for k, v in request.headers.items()
                }
            },
            'response': {
                'status_code': response.status_code,
                'header': {
                    k.lower(): v for k, v in response.headers.items()
                },
            }
        },
        'url': {
            'path': request.path or 'UNKNOWN', 'scheme': request.scheme or 'UNKNOWN'
        }
    }


class LoggedNinjaAPI(NinjaAPI):
    """Extension for the NinjaAPI to log the requests to elastic

    Overwriting the method that creates a response. The only thing done then
    is that depending on the status, a log entry will be triggered.
    """

    def create_response(
        self,
        request: HttpRequest,
        data: Any,
        *args: List[Any],
        status: Optional[int] = None,
        temporal_response: Optional[HttpResponse] = None,
    ) -> HttpResponse:
        response = super().create_response(
            request, data, *args, status=status, temporal_response=temporal_response
        )

        if response.status_code >= 200 and response.status_code < 400:
            logger.info(
                "Response %s on %s",
                response.status_code,  # parameter for %s
                request.path,  # parameter for %s
                extra=generate_log_extra(request, response)
            )
        elif response.status_code >= 400 and response.status_code < 500:
            logger.warning(
                "Response %s on %s",
                response.status_code,  # parameter for %s
                request.path,  # parameter for %s
                extra=generate_log_extra(request, response)
            )
        else:
            logger.exception(repr(sys.exc_info()[1]), extra=generate_log_extra(request, response))

        return response


api = LoggedNinjaAPI()

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
@api.exception_handler(ObjectDoesNotExist)
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


@api.exception_handler(EndpointConnectionError)
def handle_cognito_connection_error(
    request: HttpRequest, exception: EndpointConnectionError
) -> HttpResponse:
    return api.create_response(
        request,
        {
            "code": 503, "description": "Service Unavailable"
        },
        status=503,
    )


root = NinjaAPI(urls_namespace="root")


@root.get("/checker")
def checker(request: HttpRequest) -> dict[str, bool | str]:
    return {"success": True, "message": "OK"}
