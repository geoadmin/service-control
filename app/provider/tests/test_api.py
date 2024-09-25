from ninja.testing import TestClient
from provider.api import router
from provider.models import Provider

from django.test import TransactionTestCase


class ApiTestCase(TransactionTestCase):

    # Needed because we test the primary key. Otherwise the object ID a random
    # number when running multiple tests in parallel.
    reset_sequences = True

    def test_get_provider_returns_existing_provider_with_default_language(self):

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

        assert response.status_code == 200
        assert response.data == {
            "id": "1",
            "name": "Federal Office for the Environment",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
                "it": "Ufficio federale dell'ambiente",
                "rm": "Uffizi federal per l'ambient",
            },
            "acronym": "FOEN",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
                "it": "UFAM",
                "rm": "UFAM",
            }
        }

    def test_get_provider_returns_provider_with_given_language(self):

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
        response = client.get("/providers/1?lang=de")

        assert response.status_code == 200
        assert response.data == {
            "id": "1",
            "name": "Bundesamt für Umwelt",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
                "it": "Ufficio federale dell'ambiente",
                "rm": "Uffizi federal per l'ambient",
            },
            "acronym": "BAFU",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
                "it": "UFAM",
                "rm": "UFAM",
            }
        }

    def test_get_provider_returns_404_for_nonexisting_provider(self):

        client = TestClient(router)
        response = client.get("/providers/1")

        assert response.status_code == 404
        assert response.data == {"detail": "Not Found"}


    def test_get_provider_skips_translations_that_are_not_available(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        Provider.objects.create(**provider)

        client = TestClient(router)
        response = client.get("/providers/1")

        assert response.status_code == 200
        assert response.data == {
            "id": "1",
            "name": "Federal Office for the Environment",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "acronym": "FOEN",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            }
        }

