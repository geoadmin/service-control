from provider.models import Provider

from django.db import IntegrityError
from django.forms import ModelForm
from django.test import TestCase


class ProviderTestCase(TestCase):

    def test_object_created_in_db_with_all_fields_defined(self):
        provider_in = {
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

        self.assertEqual(len(providers), 1)

        actual = Provider.objects.last()
        self.assertEqual(provider_in["name_de"], actual.name_de)
        self.assertEqual(provider_in["name_fr"], actual.name_fr)
        self.assertEqual(provider_in["name_en"], actual.name_en)
        self.assertEqual(provider_in["name_it"], actual.name_it)
        self.assertEqual(provider_in["name_rm"], actual.name_rm)

        self.assertEqual(provider_in["acronym_de"], actual.acronym_de)
        self.assertEqual(provider_in["acronym_fr"], actual.acronym_fr)
        self.assertEqual(provider_in["acronym_en"], actual.acronym_en)
        self.assertEqual(provider_in["acronym_it"], actual.acronym_it)
        self.assertEqual(provider_in["acronym_rm"], actual.acronym_rm)

    def test_object_created_in_db_with_optional_fields_null(self):
        provider_in = {
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

        self.assertEqual(len(providers), 1)

        actual = Provider.objects.last()
        self.assertEqual(actual.name_de, provider_in["name_de"])
        self.assertEqual(actual.name_fr, provider_in["name_fr"])
        self.assertEqual(actual.name_en, provider_in["name_en"])
        self.assertEqual(actual.name_it, provider_in["name_it"])
        self.assertEqual(actual.name_rm, provider_in["name_rm"])

        self.assertEqual(actual.acronym_de, provider_in["acronym_de"])
        self.assertEqual(actual.acronym_fr, provider_in["acronym_fr"])
        self.assertEqual(actual.acronym_en, provider_in["acronym_en"])
        self.assertEqual(actual.acronym_it, provider_in["acronym_it"])
        self.assertEqual(actual.acronym_rm, provider_in["acronym_rm"])

    def test_raises_exception_when_creating_db_object_with_mandatory_field_null(self):
        self.assertRaises(IntegrityError, Provider.objects.create, name_de=None)

    def test_form_valid_for_blank_optional_field(self):

        class ProviderForm(ModelForm):

            class Meta:
                model = Provider
                fields = "__all__"

        data = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        form = ProviderForm(data)

        self.assertTrue(form.is_valid())

    def test_form_invalid_for_blank_mandatory_field(self):

        class ProviderForm(ModelForm):

            class Meta:
                model = Provider
                fields = "__all__"

        data = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "",  # empty but mandatory field
        }
        form = ProviderForm(data)

        self.assertFalse(form.is_valid())
