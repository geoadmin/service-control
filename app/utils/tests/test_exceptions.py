from utils.exceptions import validation_error_to_http_error

from django.core.exceptions import ValidationError


def test_validation_error_to_http_error_returns_409_for_single_unique():

    error = ValidationError({
        'field1': [ValidationError(code="unique", message="my message")],
    })
    actual = validation_error_to_http_error(error)
    assert actual.status_code == 409
    assert actual.message == "['my message']"


def test_validation_error_to_http_error_returns_422_for_single_invalid():

    error = ValidationError({
        'field1': [ValidationError(code="invalid", message="my message")],
    })
    actual = validation_error_to_http_error(error)
    assert actual.status_code == 422
    assert actual.message == "['my message']"


def test_validation_error_to_http_error_returns_409_when_at_least_one_unique():

    error = ValidationError(
        message={
            "field1": [ValidationError(code="unique", message="my message 1")],
            "field2": [ValidationError(code="invalid", message="my message 2")],
        },
    )
    actual = validation_error_to_http_error(error)
    assert actual.status_code == 409
    assert actual.message == "['my message 1', 'my message 2']"


def test_validation_error_to_http_error_returns_409_even_when_unique_burried_deep():

    error = ValidationError(
        message={
            "field1": [
                ValidationError(code="invalid", message="my message 1.1"),
                ValidationError(code="unique", message="my message 1.2"),
            ],
            "field2": [ValidationError(code="invalid", message="my message 2")],
        },
    )
    actual = validation_error_to_http_error(error)
    assert actual.status_code == 409
    assert actual.message == "['my message 1.1', 'my message 1.2', 'my message 2']"


def test_validation_error_to_http_error_returns_422_when_no_unique():

    error = ValidationError(
        message={
            "field1": [ValidationError(code="whatever", message="my message 1")],
            "field2": [ValidationError(code="invalid", message="my message 2")],
        },
    )
    actual = validation_error_to_http_error(error)
    assert actual.status_code == 422
    assert actual.message == "['my message 1', 'my message 2']"
