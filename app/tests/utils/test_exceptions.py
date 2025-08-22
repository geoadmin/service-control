from utils.exceptions import contains_error_code
from utils.exceptions import extract_error_messages

from django.core.exceptions import ValidationError


def test_contains_error_code_returns_true_for_single_error_with_matching_code():
    exception = ValidationError(message=None, code="code1")
    assert contains_error_code(exception, "code1")


def test_contains_error_code_returns_false_for_single_error_without_matching_code():
    exception = ValidationError(message=None, code="code1")
    assert not contains_error_code(exception, "code2")


def test_contains_error_code_returns_true_for_error_dict_where_one_has_matching_code():
    exception = ValidationError(
        {
            "field1": ValidationError(message=None, code="code1"),
            "field2": ValidationError(message=None, code="code2"),
        }
    )
    assert contains_error_code(exception, "code2")


def test_contains_error_code_returns_false_for_error_dict_without_matching_code():
    exception = ValidationError(
        {
            "field1": ValidationError(message=None, code="code1"),
            "field2": ValidationError(message=None, code="code2"),
        }
    )
    assert not contains_error_code(exception, "code3")


def test_contains_error_code_returns_true_for_multiple_errors_per_field():
    exception = ValidationError(
        {
            "field1": [
                ValidationError(message=None, code="code1"),
                ValidationError(message=None, code="code2"),
            ],
            "field2": [ValidationError(message=None, code="code3")],
        }
    )
    assert contains_error_code(exception, "code2")


def test_contains_error_code_returns_false_for_multiple_errors_per_field_without_matching():
    exception = ValidationError(
        {
            "field1": [
                ValidationError(message=None, code="code1"),
                ValidationError(message=None, code="code2"),
            ],
            "field2": [ValidationError(message=None, code="code3")],
        }
    )
    assert not contains_error_code(exception, "code4")


def test_contains_error_code_returns_true_for_list_of_errors():
    exception = ValidationError(
        [
            ValidationError(message=None, code="code1"),
            ValidationError(message=None, code="code2"),
        ]
    )
    assert contains_error_code(exception, "code2")


def test_contains_error_code_returns_false_for_list_of_errors_without_matching():
    exception = ValidationError(
        [
            ValidationError(message=None, code="code1"),
            ValidationError(message=None, code="code2"),
        ]
    )
    assert not contains_error_code(exception, "code3")


def test_extract_error_messages_results_in_single_element_for_single_message():
    exception = ValidationError(message="XXX")
    assert extract_error_messages(exception) == ["XXX"]


def test_extract_error_messages_results_in_empty_list_when_no_message():
    exception = ValidationError(message=None)
    assert not extract_error_messages(exception)


def test_extract_error_messages_finds_all_messages_in_dict():
    exception = ValidationError(
        {
            "field1": ValidationError(message="m1"),
            "field2": ValidationError(message="m2"),
        }
    )
    assert extract_error_messages(exception) == ["m1", "m2"]


def test_extract_error_messages_skips_undefined_messages_in_dict():
    exception = ValidationError(
        {
            "field1": ValidationError(message="m1"),
            "field2": ValidationError(message=None),
        }
    )
    assert extract_error_messages(exception) == ["m1"]


def test_extract_error_messages_finds_all_messages_in_dict_with_list():
    exception = ValidationError(
        {
            "field1": [ValidationError(message="m1"), ValidationError(message="m2")],
            "field2": [ValidationError(message="m3")],
        }
    )
    assert extract_error_messages(exception) == ["m1", "m2", "m3"]
