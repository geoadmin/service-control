"""This is a workaround to be able to test exception handling with Ninja's TestClient.

For exception handling at the level of the NinjaAPI object, normally you would
do something like this:

    @api.exception_handler(MyException)
    def handle_my_exception(request: HttpRequest, exc: MyException) -> HttpResponse:
        # convert MyException to HttpResponse

But, as Ninja's TestClient runs "without middleware/url-resolver layer", you cannot
test exception handling in a unit test. The workaround solves this by defining
an explicit function to register exception handlers.

The workaround is inspired by the answer to this ticket:
https://github.com/vitalik/django-ninja/issues/1171
"""

from collections.abc import Callable
from http import HTTPStatus

from ninja import NinjaAPI
from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.http import HttpResponse


def get_validation_error_handler(
    api: NinjaAPI
) -> tuple[Callable[[HttpRequest, ValidationError], HttpResponse], type[ValidationError]]:

    def handle(request: HttpRequest, exception: ValidationError) -> HttpResponse:
        if contains_error_code(exception, code="unique"):
            status = HTTPStatus.CONFLICT
        else:
            status = HTTPStatus.UNPROCESSABLE_ENTITY

        messages = extract_error_messages(exception)
        return api.create_response(
            request,
            {"detail": messages},
            status=status,
        )

    return (handle, ValidationError)


EXCEPTION_HANDLERS = [get_validation_error_handler]


def add_exception_handlers(api: NinjaAPI) -> None:
    for handler in EXCEPTION_HANDLERS:
        handler_func, exc = handler(api)
        api.add_exception_handler(handler=handler_func, exc_class=exc)
