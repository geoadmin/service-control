import pytest
from utils.language import LanguageCode
from utils.language import get_language
from utils.language import get_translation


def test_get_language_returns_value_of_query_param_if_defined():
    assert (
        get_language(lang_query_param="de", headers={"Accept-Language": "fr"})
        == LanguageCode.GERMAN
    )


def test_get_language_returns_value_of_header_if_query_param_undefined():
    assert (
        get_language(lang_query_param=None, headers={"Accept-Language": "fr"})
        == LanguageCode.FRENCH
    )


def test_get_language_returns_value_of_header_if_query_param_invalid_language():
    assert (
        get_language(lang_query_param="es", headers={"Accept-Language": "rm"})
        == LanguageCode.ROMANSH
    )


def test_get_language_returns_default_if_header_empty():
    assert (
        get_language(lang_query_param=None, headers={"Accept-Language": ""})
        == LanguageCode.ENGLISH
    )


def test_get_language_returns_default_if_language_header_absent():
    assert (
        get_language(lang_query_param=None, headers={"test": ""})
        == LanguageCode.ENGLISH
    )


def test_get_translation_returns_correct_field_if_present():
    class TestClass:
        field1_de = None
        field1_en = "my field"
        field2_de = None

    test = TestClass()

    actual = get_translation(obj=test, field_name="field1", lang="en")

    assert actual == "my field"


def test_get_translation_returns_default_if_field_absent():
    class TestClass:
        field1_en = "my field"

    test = TestClass()

    actual = get_translation(
        obj=test, field_name="field1", lang="de", default_lang="en"
    )

    assert actual == "my field"


def test_get_translation_returns_default_if_field_empty():
    class TestClass:
        field1_de = ""
        field1_en = "my field"

    test = TestClass()

    actual = get_translation(
        obj=test, field_name="field1", lang="de", default_lang="en"
    )

    assert actual == "my field"


def test_get_translation_returns_default_if_field_none():
    class TestClass:
        field1_de = None
        field1_en = "my field"

    test = TestClass()

    actual = get_translation(
        obj=test, field_name="field1", lang="de", default_lang="en"
    )

    assert actual == "my field"


def test_get_translation_raises_exception_if_even_default_field_absent():
    class TestClass:
        field1_it = None

    test = TestClass()

    with pytest.raises(AttributeError):
        get_translation(obj=test, field_name="field1", lang="de", default_lang="en")


def test_get_translation_raises_exception_if_even_default_field_empty():
    class TestClass:
        field1_en = ""

    test = TestClass()

    with pytest.raises(AttributeError):
        get_translation(obj=test, field_name="field1", lang="de", default_lang="en")


def test_get_translation_raises_exception_if_even_default_field_none():
    class TestClass:
        field1_en = None

    test = TestClass()

    with pytest.raises(AttributeError):
        get_translation(obj=test, field_name="field1", lang="de", default_lang="en")
