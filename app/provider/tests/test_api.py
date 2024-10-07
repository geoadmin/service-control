from ninja.testing import TestClient
from provider.api import router
from provider.api import to_response
from provider.models import Provider
from provider.schemas import ProviderSchema
from schemas import TranslationsSchema

from django.test import TestCase


class ApiTestCase(TestCase):

    def test_to_response_returns_response_with_language_as_defined(self):
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
        model = Provider.objects.create(**model_fields)

        actual = to_response(model, lang="de")

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

    def test_to_response_returns_response_with_default_language_if_undefined(self):
        model_fields = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        model = Provider.objects.create(**model_fields)

        actual = to_response(model, lang="it")

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
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
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

    def test_get_provider_returns_provider_with_language_from_query(self):

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
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}?lang=de")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
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
        response = client.get("/1")

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
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
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

    def test_get_provider_returns_provider_with_language_from_header(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
            "name": "Bundesamt für Umwelt",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "acronym": "BAFU",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            }
        }

    def test_get_provider_returns_provider_with_language_from_query_param_even_if_header_set(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}?lang=fr", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
            "name": "Office fédéral de l'environnement",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "acronym": "OFEV",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            }
        }

    def test_get_provider_returns_provider_with_default_language_if_header_empty(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}", headers={"Accept-Language": ""})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
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

    def test_get_provider_returns_provider_with_first_known_language_from_header(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}", headers={"Accept-Language": "cn, *, de-DE, en"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
            "name": "Bundesamt für Umwelt",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "acronym": "BAFU",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            }
        }

    def test_get_provider_returns_provider_with_first_known_language_from_header_ignoring_qfactor(
        self
    ):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get(f"/{provider_id}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{provider_id}",
            "name": "Office fédéral de l'environnement",
            "name_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "acronym": "OFEV",
            "acronym_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            }
        }

    def test_get_providers_returns_single_provider_with_given_language(self):

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
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get("/?lang=fr")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "id": f"{provider_id}",
                "name": "Office fédéral de l'environnement",
                "name_translations": {
                    "de": "Bundesamt für Umwelt",
                    "fr": "Office fédéral de l'environnement",
                    "en": "Federal Office for the Environment",
                    "it": "Ufficio federale dell'ambiente",
                    "rm": "Uffizi federal per l'ambient",
                },
                "acronym": "OFEV",
                "acronym_translations": {
                    "de": "BAFU",
                    "fr": "OFEV",
                    "en": "FOEN",
                    "it": "UFAM",
                    "rm": "UFAM",
                }
            }]
        }

    def test_get_providers_skips_translations_that_are_not_available(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get("/")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "id": f"{provider_id}",
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
            }]
        }

    def test_get_providers_returns_provider_with_language_from_header(self):

        provider = {
            "name_de": "Bundesamt für Umwelt",
            "name_fr": "Office fédéral de l'environnement",
            "name_en": "Federal Office for the Environment",
            "acronym_de": "BAFU",
            "acronym_fr": "OFEV",
            "acronym_en": "FOEN",
        }
        provider_id = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get("/", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "id": f"{provider_id}",
                "name": "Bundesamt für Umwelt",
                "name_translations": {
                    "de": "Bundesamt für Umwelt",
                    "fr": "Office fédéral de l'environnement",
                    "en": "Federal Office for the Environment",
                },
                "acronym": "BAFU",
                "acronym_translations": {
                    "de": "BAFU",
                    "fr": "OFEV",
                    "en": "FOEN",
                }
            }]
        }

    def test_get_providers_returns_all_providers_ordered_by_id_with_given_language(self):

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
        provider_id_1 = Provider.objects.create(**provider).id

        provider = {
            "name_de": "Bundesamt für Verkehr",
            "name_fr": "Office fédéral des transports",
            "name_en": "Federal Office of Transport",
            "name_it": "Ufficio federale dei trasporti",
            "name_rm": "Uffizi federal da traffic",
            "acronym_de": "BAV",
            "acronym_fr": "OFT",
            "acronym_en": "FOT",
            "acronym_it": "UFT",
            "acronym_rm": "UFT",
        }
        provider_id_2 = Provider.objects.create(**provider).id

        client = TestClient(router)
        response = client.get("/?lang=fr")

        assert response.status_code == 200
        assert response.data == {
            "items": [
                {
                    "id": f"{provider_id_1}",
                    "name": "Office fédéral de l'environnement",
                    "name_translations": {
                        "de": "Bundesamt für Umwelt",
                        "fr": "Office fédéral de l'environnement",
                        "en": "Federal Office for the Environment",
                        "it": "Ufficio federale dell'ambiente",
                        "rm": "Uffizi federal per l'ambient",
                    },
                    "acronym": "OFEV",
                    "acronym_translations": {
                        "de": "BAFU",
                        "fr": "OFEV",
                        "en": "FOEN",
                        "it": "UFAM",
                        "rm": "UFAM",
                    }
                },
                {
                    "id": f"{provider_id_2}",
                    "name": "Office fédéral des transports",
                    "name_translations": {
                        "de": "Bundesamt für Verkehr",
                        "fr": "Office fédéral des transports",
                        "en": "Federal Office of Transport",
                        "it": "Ufficio federale dei trasporti",
                        "rm": "Uffizi federal da traffic",
                    },
                    "acronym": "OFT",
                    "acronym_translations": {
                        "de": "BAV",
                        "fr": "OFT",
                        "en": "FOT",
                        "it": "UFT",
                        "rm": "UFT",
                    }
                },
            ]
        }
