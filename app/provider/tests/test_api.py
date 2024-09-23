from ninja.testing import TestClient
from provider.api import router
from provider.models import Provider

from django.test import TestCase


class ApiTestCase(TestCase):

    def test_get_provider_returns_existing_provider(self):

        provider = {
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
        Provider.objects.create(**provider)

        client = TestClient(router)
        response = client.get("/providers/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "id": "1",
                "name_translations": {
                    "de": "Bundesamt für Umwelt",
                    "fr": "Office fédéral de l'environnement",
                    "en": "Federal Office for the Environment",
                    "it": "Ufficio federale dell'ambiente",
                    "rm": "Uffizi federal per l'ambient",
                },
                "acronym_translations": {
                    "de": "BAFU", "fr": "OFEV", "en": "FOEN", "it": "UFAM", "rm": "UFAM",
                }
            }
        )
