import pytest
from utils.translation import get_translation


class TestMultilangModel:

    def test_get_translation_returns_correct_field_if_present(self):

        class TestClass:
            field1_de: str
            field1_en: str = "my field"
            field2_de: str

        test = TestClass()

        actual = get_translation(obj=test, field_name="field1", lang="en")

        assert actual == "my field"

    def test_get_translation_returns_default_if_field_absent(self):

        class TestClass:
            field1_en: str = "my field"

        test = TestClass()

        actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

        assert actual == "my field"

    def test_get_translation_returns_default_if_field_empty(self):

        class TestClass:
            field1_de: str = ""
            field1_en: str = "my field"

        test = TestClass()

        actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

        assert actual == "my field"

    def test_get_translation_returns_default_if_field_none(self):

        class TestClass:
            field1_de: str = None
            field1_en: str = "my field"

        test = TestClass()

        actual = get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

        assert actual == "my field"

    def test_get_translation_raises_exception_if_even_default_field_absent(self):

        class TestClass:
            field1_it: str

        test = TestClass()

        with pytest.raises(AttributeError):
            get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

    def test_get_translation_raises_exception_if_even_default_field_empty(self):

        class TestClass:
            field1_en: str = ""

        test = TestClass()

        with pytest.raises(AttributeError):
            get_translation(obj=test, field_name="field1", lang="de", default_lang="en")

    def test_get_translation_raises_exception_if_even_default_field_none(self):

        class TestClass:
            field1_en: str = None

        test = TestClass()

        with pytest.raises(AttributeError):
            get_translation(obj=test, field_name="field1", lang="de", default_lang="en")
