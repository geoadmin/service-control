from provider.api import provider_to_response
from provider.models import Provider
from provider.schemas import ProviderSchema
from schemas import TranslationsSchema
from utils.testing import create_user_with_permissions

from django.test import TestCase


class ApiTestCase(TestCase):

    def setUp(self):
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

    def test_provider_to_response_returns_response_with_language_as_defined(self):

        model = Provider.objects.last()

        actual = provider_to_response(model, lang="de")

        expected = ProviderSchema(
            id=model.id,
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

    def test_provider_to_response_returns_response_with_default_language_if_undefined(self):

        provider = Provider.objects.last()
        provider.name_it = None
        provider.name_rm = None
        provider.acronym_it = None
        provider.acronym_rm = None

        actual = provider_to_response(provider, lang="it")

        expected = ProviderSchema(
            id=str(provider.id),
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(f"/api/providers/{provider_id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(f"/api/providers/{provider_id}?lang=de")

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/providers/2")

        assert response.status_code == 404
        assert response.json() == {"code": 404, "description": "Resource not found"}

    def test_get_provider_skips_translations_that_are_not_available(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider = Provider.objects.last()
        provider.name_it = None
        provider.name_rm = None
        provider.acronym_it = None
        provider.acronym_rm = None
        provider.save()

        response = self.client.get(f"/api/providers/{provider.id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": provider.id,
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(
            f"/api/providers/{provider_id}", headers={"Accept-Language": "de"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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

    def test_get_provider_returns_provider_with_language_from_query_param_even_if_header_set(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(
            f"/api/providers/{provider_id}?lang=fr", headers={"Accept-Language": "de"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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
        }

    def test_get_provider_returns_provider_with_default_language_if_header_empty(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(f"/api/providers/{provider_id}", headers={"Accept-Language": ""})

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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

    def test_get_provider_returns_provider_with_first_known_language_from_header(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(
            f"/api/providers/{provider_id}", headers={"Accept-Language": "cn, *, de-DE, en"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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

    def test_get_provider_returns_provider_with_first_known_language_from_header_ignoring_qfactor(
        self
    ):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id

        response = self.client.get(
            f"/api/providers/{provider_id}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": provider_id,
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
        }

    def test_get_provider_returns_401_if_not_logged_in(self):
        provider_id = Provider.objects.last().id
        response = self.client.get(f"/api/providers/{provider_id}")

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}

    def test_get_provider_returns_403_if_no_permission(self):
        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        provider_id = Provider.objects.last().id
        response = self.client.get(f"/api/providers/{provider_id}")

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}

    def test_get_providers_returns_single_provider_with_given_language(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/providers?lang=fr")

        assert response.status_code == 200
        assert response.json() == {
            "items": [{
                "id": Provider.objects.last().id,
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        provider = Provider.objects.last()
        provider.name_it = None
        provider.name_rm = None
        provider.acronym_it = None
        provider.acronym_rm = None
        provider.save()

        response = self.client.get("/api/providers")

        assert response.status_code == 200
        assert response.json() == {
            "items": [{
                "id": provider.id,
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
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/providers", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.json() == {
            "items": [{
                "id": Provider.objects.last().id,
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
            }]
        }

    def test_get_providers_returns_all_providers_ordered_by_id_with_given_language(self):
        create_user_with_permissions('test', 'test', [('provider', 'provider', 'view_provider')])
        self.client.login(username='test', password='test')

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
        Provider.objects.create(**provider)

        response = self.client.get("/api/providers?lang=fr")

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": Provider.objects.first().id,
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
                    "id": Provider.objects.last().id,
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

    def test_get_providers_returns_401_if_not_logged_in(self):
        response = self.client.get("/api/providers")

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}

    def test_get_providers_returns_403_if_no_permission(self):
        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/providers")

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}
