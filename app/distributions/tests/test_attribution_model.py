from distributions.models import Attribution
from provider.models import Provider

from django.forms import ModelForm
from django.test import TestCase


class AttributionTestCase(TestCase):

    def test_simple_model_creation(self):
        name_de = "BAFU"
        name_fr = "OFEV"
        name_en = "FOEN"
        name_it = "UFAM"
        name_rm = "UFAM"
        description_de = "Bundesamt für Umwelt"
        description_fr = "Office fédéral de l'environnement"
        description_en = "Federal Office for the Environment"
        description_it = "Ufficio federale dell'ambiente"
        description_rm = "Uffizi federal per l'ambient"

        provider = Provider.objects.create(acronym_de="ENSI")

        Attribution.objects.create(
            name_de=name_de,
            name_fr=name_fr,
            name_en=name_en,
            name_it=name_it,
            name_rm=name_rm,
            description_de=description_de,
            description_fr=description_fr,
            description_en=description_en,
            description_it=description_it,
            description_rm=description_rm,
            provider=provider
        )

        attributions = Attribution.objects.all()

        self.assertEqual(len(attributions), 1)

        attribution = Attribution.objects.last()
        self.assertEqual(attribution.name_de, name_de)
        self.assertEqual(attribution.name_fr, name_fr)
        self.assertEqual(attribution.name_en, name_en)
        self.assertEqual(attribution.name_it, name_it)
        self.assertEqual(attribution.name_rm, name_rm)

        self.assertEqual(attribution.description_de, description_de)
        self.assertEqual(attribution.description_fr, description_fr)
        self.assertEqual(attribution.description_en, description_en)
        self.assertEqual(attribution.description_it, description_it)
        self.assertEqual(attribution.description_rm, description_rm)

        self.assertEqual(attribution.provider.acronym_de, "ENSI")

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
