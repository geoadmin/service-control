from provider.models import Provider
from pytest import raises

from django.core.exceptions import ValidationError
from django.forms import ModelForm


def test_object_created_in_db_with_all_fields_defined(db):
    provider_in = {
        "provider_id": "ch.bafu",
        "name_de": "Bundesamt für Umwelt",
        "name_fr": "Office fédéral de l'environnement",
        "name_en": "Federal Office for the Environment",
        "name_it": "Ufficio federale dell'ambiente",
        "name_rm": "Uffizi federal per l'ambient",
        "acronym_de": "BAFU",
        "acronym_fr": "OFEV",
        "acronym_en": "FOEN",
        "acronym_it": "UFAM",
        "acronym_rm": "UFAM",
    }
    Provider.objects.create(**provider_in)

    providers = Provider.objects.all()

    assert len(providers) == 1

    actual = Provider.objects.last()
    assert provider_in["name_de"] == actual.name_de
    assert provider_in["name_fr"] == actual.name_fr
    assert provider_in["name_en"] == actual.name_en
    assert provider_in["name_it"] == actual.name_it
    assert provider_in["name_rm"] == actual.name_rm

    assert provider_in["acronym_de"] == actual.acronym_de
    assert provider_in["acronym_fr"] == actual.acronym_fr
    assert provider_in["acronym_en"] == actual.acronym_en
    assert provider_in["acronym_it"] == actual.acronym_it
    assert provider_in["acronym_rm"] == actual.acronym_rm


def test_object_created_in_db_with_optional_fields_null(db):
    provider_in = {
        "provider_id": "ch.bafu",
        "name_de": "Bundesamt für Umwelt",
        "name_fr": "Office fédéral de l'environnement",
        "name_en": "Federal Office for the Environment",
        "name_it": None,
        "name_rm": None,
        "acronym_de": "BAFU",
        "acronym_fr": "OFEV",
        "acronym_en": "FOEN",
        "acronym_it": None,
        "acronym_rm": None,
    }
    Provider.objects.create(**provider_in)

    providers = Provider.objects.all()

    assert len(providers) == 1

    actual = Provider.objects.last()
    assert actual.provider_id == provider_in["provider_id"]

    assert actual.name_de == provider_in["name_de"]
    assert actual.name_fr == provider_in["name_fr"]
    assert actual.name_en == provider_in["name_en"]
    assert actual.name_it == provider_in["name_it"]
    assert actual.name_rm == provider_in["name_rm"]

    assert actual.acronym_de == provider_in["acronym_de"]
    assert actual.acronym_fr == provider_in["acronym_fr"]
    assert actual.acronym_en == provider_in["acronym_en"]
    assert actual.acronym_it == provider_in["acronym_it"]
    assert actual.acronym_rm == provider_in["acronym_rm"]


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(db):
    with raises(ValidationError):
        Provider.objects.create(name_de=None)


def test_form_valid_for_blank_optional_field(db):

    class ProviderForm(ModelForm):

        class Meta:
            model = Provider
            fields = "__all__"

    data = {
        "provider_id": "ch.bafu",
        "name_de": "Bundesamt für Umwelt",
        "name_fr": "Office fédéral de l'environnement",
        "name_en": "Federal Office for the Environment",
        "acronym_de": "BAFU",
        "acronym_fr": "OFEV",
        "acronym_en": "FOEN",
    }
    form = ProviderForm(data)

    assert form.is_valid() is True


def test_form_invalid_for_blank_mandatory_field(db):

    class ProviderForm(ModelForm):

        class Meta:
            model = Provider
            fields = "__all__"

    data = {
        "provider_id": "ch.bafu",
        "name_de": "Bundesamt für Umwelt",
        "name_fr": "Office fédéral de l'environnement",
        "name_en": "Federal Office for the Environment",
        "acronym_de": "BAFU",
        "acronym_fr": "OFEV",
        "acronym_en": "",  # empty but mandatory field
    }
    form = ProviderForm(data)

    assert form.is_valid() is False
