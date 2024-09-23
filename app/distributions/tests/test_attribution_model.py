from distributions.models import Attribution
from provider.models import Provider

from django.db import IntegrityError
from django.forms import ModelForm
from django.test import TestCase


class AttributionTestCase(TestCase):

    def test_object_created_in_db_with_all_fields_defined(self):
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
            "provider": Provider.objects.create(acronym_de="ENSI")
        }
        Attribution.objects.create(**attribution)

        attributions = Attribution.objects.all()

        self.assertEqual(len(attributions), 1)

        actual = Attribution.objects.last()
        self.assertEqual(actual.name_de, attribution["name_de"])
        self.assertEqual(actual.name_fr, attribution["name_fr"])
        self.assertEqual(actual.name_en, attribution["name_en"])
        self.assertEqual(actual.name_it, attribution["name_it"])
        self.assertEqual(actual.name_rm, attribution["name_rm"])

        self.assertEqual(actual.description_de, attribution["description_de"])
        self.assertEqual(actual.description_fr, attribution["description_fr"])
        self.assertEqual(actual.description_en, attribution["description_en"])
        self.assertEqual(actual.description_it, attribution["description_it"])
        self.assertEqual(actual.description_rm, attribution["description_rm"])

        self.assertEqual(actual.provider.acronym_de, "ENSI")

    def test_object_created_in_db_with_optional_fields_null(self):
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
            "provider": Provider.objects.create(acronym_de="ENSI")
        }
        Attribution.objects.create(**attribution)

        attributions = Attribution.objects.all()

        self.assertEqual(len(attributions), 1)

        actual = Attribution.objects.last()
        self.assertEqual(actual.name_de, attribution["name_de"])
        self.assertEqual(actual.name_fr, attribution["name_fr"])
        self.assertEqual(actual.name_en, attribution["name_en"])
        self.assertEqual(actual.name_it, attribution["name_it"])
        self.assertEqual(actual.name_rm, attribution["name_rm"])

        self.assertEqual(actual.description_de, attribution["description_de"])
        self.assertEqual(actual.description_fr, attribution["description_fr"])
        self.assertEqual(actual.description_en, attribution["description_en"])
        self.assertEqual(actual.description_it, attribution["description_it"])
        self.assertEqual(actual.description_rm, attribution["description_rm"])

    def test_raises_exception_when_creating_db_object_with_mandatory_field_null(self):
        provider = Provider.objects.create()
        self.assertRaises(
            IntegrityError, Attribution.objects.create, name_de=None, provider=provider
        )

    def test_form_valid_for_blank_optional_field(self):

        class AttributionForm(ModelForm):

            class Meta:
                model = Attribution
                fields = "__all__"

        provider = Provider.objects.create()

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

        self.assertTrue(form.is_valid())

    def test_form_invalid_for_blank_mandatory_field(self):

        class AttributionForm(ModelForm):

            class Meta:
                model = Attribution
                fields = "__all__"

        provider = Provider.objects.create()

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

        self.assertFalse(form.is_valid())
