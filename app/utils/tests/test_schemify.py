from provider.models import Provider
from provider.schemas import ProviderSchema
from provider.schemas import TranslationsSchema
from utils.schemify import ProviderModelMapper

from django.test import TestCase


class ProviderModelMapperTest(TestCase):

    def test_to_schema_returns_schema_with_language_as_defined(self):
        model_fields = {
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
        Provider.objects.create(**model_fields)
        model = Provider.objects.last()

        actual = ProviderModelMapper.to_schema(model, lang="de")

        expected = ProviderSchema(
            id=str(model.id),
            name="Bundesamt für Umwelt",
            name_translations=TranslationsSchema(
                de="Bundesamt für Umwelt",
                fr="Office fédéral de l'environnement",
                en="Federal Office for the Environment",
                it="Ufficio federale dell'ambiente",
                rm="Uffizi federal per l'ambient",
            ),
            acronym="BAFU",
            acronym_translations=TranslationsSchema(
                de="BAFU",
                fr="OFEV",
                en="FOEN",
                it="UFAM",
                rm="UFAM",
            )
        )

        assert actual == expected

    def test_to_schema_returns_schema_with_default_language_if_undefined(self):
        model_fields = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        Provider.objects.create(**model_fields)
        model = Provider.objects.last()

        actual = ProviderModelMapper.to_schema(model, lang="it")

        expected = ProviderSchema(
            id=str(model.id),
            name="Federal Office for the Environment",
            name_translations=TranslationsSchema(
                de="Bundesamt für Umwelt",
                fr="Office fédéral de l'environnement",
                en="Federal Office for the Environment",
                it=None,
                rm=None,
            ),
            acronym="FOEN",
            acronym_translations=TranslationsSchema(
                de="BAFU",
                fr="OFEV",
                en="FOEN",
                it=None,
                rm=None,
            )
        )

        assert actual == expected
