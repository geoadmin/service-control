from ninja.errors import HttpError

from django.core.exceptions import ValidationError


def validation_error_to_http_error(error: ValidationError) -> HttpError:
    """Create a HttpError out of the relevant part of a Django ValidationError.

    This assumes that the ValidationError has attribute error_dict set, as it
    is done in model validation.

    The returned HttpError has its HTTP status code set to

        - 409 (Conflict) if there is an error indicating that a unique constraint is violated
        - 422 (Unprocessable Content) if there are no unique constraint violations

    The message in HttpError is the raw list of messages in the ValidationError, for example:

        "['Enter a valid email address.', 'User with this User name already exists.']"
    """
    for errors_field in error.error_dict.values():
        for error_inner in errors_field:
            if error_inner.code == 'unique':
                return HttpError(status_code=409, message=str(error.messages))

    return HttpError(status_code=422, message=str(error.messages))
