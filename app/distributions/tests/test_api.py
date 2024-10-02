from distributions.api import router
from distributions.api import to_response
from distributions.models import Attribution
from distributions.schemas import AttributionSchema
from ninja.testing import TestClient
from provider.models import Provider
from schemas import TranslationsSchema

from django.test import TestCase


class ApiTestCase(TestCase):

    def test_to_response_returns_response_with_language_as_defined(self):
        provider = Provider.objects.create()
        model_fields = {
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
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        model = Attribution.objects.last()

        actual = to_response(model, lang="de")

        expected = AttributionSchema(
            id=str(model.id),
            name="BAFU",
            name_translations=TranslationsSchema(
                de="BAFU",
                fr="OFEV",
                en="FOEN",
                it="UFAM",
                rm="UFAM",
            ),
            description="Bundesamt für Umwelt",
            description_translations=TranslationsSchema(
                de="Bundesamt für Umwelt",
                fr="Office fédéral de l'environnement",
                en="Federal Office for the Environment",
                it="Ufficio federale dell'ambiente",
                rm="Uffizi federal per l'ambient",
            ),
            provider_id=str(provider.id)
        )

        assert actual == expected

    def test_to_response_returns_response_with_default_language_if_undefined(self):
        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider
        }
        Attribution.objects.create(**model_fields)
        model = Attribution.objects.last()

        actual = to_response(model, lang="it")

        expected = AttributionSchema(
            id=str(model.id),
            name="FOEN",
            name_translations=TranslationsSchema(
                de="BAFU",
                fr="OFEV",
                en="FOEN",
                it=None,
                rm=None,
            ),
            description="Federal Office for the Environment",
            description_translations=TranslationsSchema(
                de="Bundesamt für Umwelt",
                fr="Office fédéral de l'environnement",
                en="Federal Office for the Environment",
                it=None,
                rm=None,
            ),
            provider_id=str(provider.id),
        )

        assert actual == expected

    def test_get_attribution_returns_existing_attribution_with_default_language(self):

        provider = Provider.objects.create()
        model_fields = {
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
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "FOEN",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
                "it": "UFAM",
                "rm": "UFAM",
            },
            "description": "Federal Office for the Environment",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
                "it": "Ufficio federale dell'ambiente",
                "rm": "Uffizi federal per l'ambient",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_language_from_query(self):

        provider = Provider.objects.create()
        model_fields = {
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
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}?lang=de")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "BAFU",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
                "it": "UFAM",
                "rm": "UFAM",
            },
            "description": "Bundesamt für Umwelt",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
                "it": "Ufficio federale dell'ambiente",
                "rm": "Uffizi federal per l'ambient",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_404_for_nonexisting_attribution(self):

        client = TestClient(router)
        response = client.get("/1")

        assert response.status_code == 404
        assert response.data == {"detail": "Not Found"}

    def test_get_attribution_skips_translations_that_are_not_available(self):

        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "FOEN",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Federal Office for the Environment",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_language_from_header(self):

        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "BAFU",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Bundesamt für Umwelt",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_language_from_query_param_even_if_header_set(
        self
    ):

        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}?lang=fr", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "OFEV",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Office fédéral de l'environnement",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_default_language_if_header_empty(self):

        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}", headers={"Accept-Language": ""})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "FOEN",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Federal Office for the Environment",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_first_known_language_from_header(self):

        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{attribution_id}", headers={"Accept-Language": "cn, *, de-DE, en"})

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "BAFU",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Bundesamt für Umwelt",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }

    def test_get_attribution_returns_attribution_with_first_language_from_header_ignoring_qfactor(
        self
    ):
        provider = Provider.objects.create()
        model_fields = {
            "name_de": "BAFU",
            "name_fr": "OFEV",
            "name_en": "FOEN",
            "description_de": "Bundesamt für Umwelt",
            "description_fr": "Office fédéral de l'environnement",
            "description_en": "Federal Office for the Environment",
            "provider": provider,
        }
        Attribution.objects.create(**model_fields)
        attribution_id = Attribution.objects.last().id

        client = TestClient(router)
        response = client.get(
            f"/{attribution_id}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
        )

        assert response.status_code == 200
        assert response.data == {
            "id": f"{attribution_id}",
            "name": "OFEV",
            "name_translations": {
                "de": "BAFU",
                "fr": "OFEV",
                "en": "FOEN",
            },
            "description": "Office fédéral de l'environnement",
            "description_translations": {
                "de": "Bundesamt für Umwelt",
                "fr": "Office fédéral de l'environnement",
                "en": "Federal Office for the Environment",
            },
            "provider_id": str(provider.id),
        }
