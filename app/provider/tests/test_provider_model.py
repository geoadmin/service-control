from provider.models import Provider

from django.forms import ModelForm
from django.test import TestCase


class ProviderTestCase(TestCase):

    def test_model_creation_as_expected_when_all_fields_defined(self):
        name_de = "Bundesamt für Umwelt"
        name_fr = "Office fédéral de l'environnement"
        name_en = "Federal Office for the Environment"
        name_it = "Ufficio federale dell'ambiente"
        name_rm = "Uffizi federal per l'ambient"
        acronym_de = "BAFU"
        acronym_fr = "OFEV"
        acronym_en = "FOEN"
        acronym_it = "UFAM"
        acronym_rm = "UFAM"
        Provider.objects.create(
            name_de=name_de,
            name_fr=name_fr,
            name_en=name_en,
            name_it=name_it,
            name_rm=name_rm,
            acronym_de=acronym_de,
            acronym_fr=acronym_fr,
            acronym_en=acronym_en,
            acronym_it=acronym_it,
            acronym_rm=acronym_rm,
        )

        providers = Provider.objects.all()

        self.assertEqual(len(providers), 1)

        provider = Provider.objects.last()
        self.assertEqual(provider.name_de, name_de)
        self.assertEqual(provider.name_fr, name_fr)
        self.assertEqual(provider.name_en, name_en)
        self.assertEqual(provider.name_it, name_it)
        self.assertEqual(provider.name_rm, name_rm)

        self.assertEqual(provider.acronym_de, acronym_de)
        self.assertEqual(provider.acronym_fr, acronym_fr)
        self.assertEqual(provider.acronym_en, acronym_en)
        self.assertEqual(provider.acronym_it, acronym_it)
        self.assertEqual(provider.acronym_rm, acronym_rm)


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
