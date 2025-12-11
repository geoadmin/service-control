import sys
from logging import getLogger
from time import time
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import TypedDict

from ninja import NinjaAPI

from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse

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
                    k.lower(): v
                    for k, v in request.headers.items()
                    if k.lower() in settings.LOG_ALLOWED_HEADERS
                }
            },
            'response': {
                'status_code': response.status_code,
                'header': {
                    k.lower(): v
                    for k, v in response.headers.items()
                    if k.lower() in settings.LOG_ALLOWED_HEADERS
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


class RequestResponseLoggingMiddleware:
    url_safe = ',:/'  # characters that should not be urlencoded in the log statements

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Do not log API calls, they are logged with the LoggedNinjaAPI above
        if request.path.startswith('/api/'):
            return self.get_response(request)

        # Code to be executed for each request before the view (and later middlewares) are called.
        method = (request.method or '').upper()
        extra: dict[str, Any] = {
            "request.request": request, "request.query": request.GET.urlencode(self.url_safe)
        }
        add_payload = (
            method in ("PATCH", "POST", "PUT") and request.content_type == "application/json"
        )
        if add_payload:
            payload = request.body.decode()[:int(settings.LOGGING_MAX_REQUEST_PAYLOAD_SIZE)]
            extra["request.payload"] = payload

        logger.debug(
            "Request %s %s?%s",
            method,
            request.path,
            request.GET.urlencode(self.url_safe),
            extra=extra
        )
        start = time()

        response = self.get_response(request)

        # Code to be executed for each request/response after the view is called.
        extra = {
            "request": request,
            "response": {
                "code": response.status_code,
                "headers": dict(response.items()),
                "duration": time() - start
            },
        }

        # Not all response types have a 'content' attribute, HttpResponse and JSONResponse sure have
        # (e.g. WhiteNoiseFileResponse doesn't)
        if isinstance(response, (HttpResponse, JsonResponse)):
            payload = response.content.decode()[:int(settings.LOGGING_MAX_RESPONSE_PAYLOAD_SIZE)]
            extra["response"]["payload"] = payload

        logger.info(
            "Response %s %s %s?%s",
            response.status_code,
            method,
            request.path,
            request.GET.urlencode(RequestResponseLoggingMiddleware.url_safe),
            extra=extra
        )

        return response
