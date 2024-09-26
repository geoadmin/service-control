import pytest
from utils.language import get_translation


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

    actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

    assert actual == "my field"


def test_get_translation_returns_default_if_field_empty():

    class TestClass:
        field1_de = ""
        field1_en = "my field"

    test = TestClass()

    actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

    assert actual == "my field"


def test_get_translation_returns_default_if_field_none():

    class TestClass:
        field1_de = None
        field1_en = "my field"

    test = TestClass()

    actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

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
