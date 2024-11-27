from distributions.models import Attribution
from provider.models import Provider
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError
from django.forms import ModelForm


@fixture(name='provider')
def fixture_provider(db):
    yield Provider.objects.create(
        acronym_de="BAFU",
        acronym_fr="OFEV",
        acronym_en="FOEN",
        name_de="Bundesamt für Umwelt",
        name_fr="Office fédéral de l'environnement",
        name_en="Federal Office for the Environment"
    )


def test_object_created_in_db_with_all_fields_defined(provider):
    attribution = {
        "name_de": "BAFU",
        "name_fr": "OFEV",
        "name_en": "FOEN",
        "name_it": "UFAM",
        "name_rm": "UFAM",
        "description_de": "Bundesamt für Umwelt",
        "description_fr": "Office fédéral de l'environnement",
        "description_en": "Federal Office for the Environment",
        "description_it": "Ufficio federale dell'ambiente",
        "description_rm": "Uffizi federal per l'ambient",
        "provider": provider
    }
    Attribution.objects.create(**attribution)

    attributions = Attribution.objects.all()

    assert len(attributions) == 1

    actual = Attribution.objects.last()
    assert actual.name_de == attribution["name_de"]
    assert actual.name_fr == attribution["name_fr"]
    assert actual.name_en == attribution["name_en"]
    assert actual.name_it == attribution["name_it"]
    assert actual.name_rm == attribution["name_rm"]

    assert actual.description_de == attribution["description_de"]
    assert actual.description_fr == attribution["description_fr"]
    assert actual.description_en == attribution["description_en"]
    assert actual.description_it == attribution["description_it"]
    assert actual.description_rm == attribution["description_rm"]

    assert actual.provider.acronym_de == "BAFU"


def test_object_created_in_db_with_optional_fields_null(provider):
    attribution = {
        "name_de": "BAFU",
        "name_fr": "OFEV",
        "name_en": "FOEN",
        "name_it": None,
        "name_rm": None,
        "description_de": "Bundesamt für Umwelt",
        "description_fr": "Office fédéral de l'environnement",
        "description_en": "Federal Office for the Environment",
        "description_it": None,
        "description_rm": None,
        "provider": provider
    }
    Attribution.objects.create(**attribution)

    attributions = Attribution.objects.all()

    assert len(attributions) == 1

    actual = Attribution.objects.last()
    assert actual.name_de == attribution["name_de"]
    assert actual.name_fr == attribution["name_fr"]
    assert actual.name_en == attribution["name_en"]
    assert actual.name_it == attribution["name_it"]
    assert actual.name_rm == attribution["name_rm"]

    assert actual.description_de == attribution["description_de"]
    assert actual.description_fr == attribution["description_fr"]
    assert actual.description_en == attribution["description_en"]
    assert actual.description_it == attribution["description_it"]
    assert actual.description_rm == attribution["description_rm"]


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(provider):
    with raises(ValidationError):
        Attribution.objects.create(name_de=None, provider=provider)


def test_form_valid_for_blank_optional_field(provider):

    class AttributionForm(ModelForm):

        class Meta:
            model = Attribution
            fields = "__all__"

    data = {
        "name_de": "BAFU",
        "name_fr": "OFEV",
        "name_en": "FOEN",
        "description_de": "Bundesamt für Umwelt",
        "description_fr": "Office fédéral de l'environnement",
        "description_en": "Federal Office for the Environment",
        "provider": provider.id,
    }
    form = AttributionForm(data)

    assert form.is_valid() is True


def test_form_invalid_for_blank_mandatory_field(provider):

    class AttributionForm(ModelForm):

        class Meta:
            model = Attribution
            fields = "__all__"

    data = {
        "name_de": "BAFU",
        "name_fr": "OFEV",
        "name_en": "FOEN",
        "description_de": "Bundesamt für Umwelt",
        "description_fr": "Office fédéral de l'environnement",
        "description_en": "",  # empty but mandatory field
        "provider": provider.id,
    }
    form = AttributionForm(data)

    assert form.is_valid() is False
