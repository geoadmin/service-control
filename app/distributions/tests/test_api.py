import datetime
from unittest import mock

from distributions.api import attribution_to_response
from distributions.api import dataset_to_response
from distributions.api import router
from distributions.models import Attribution
from distributions.models import Dataset
from distributions.schemas import AttributionSchema
from distributions.schemas import DatasetSchema
from ninja.testing import TestClient
from provider.models import Provider
from schemas import TranslationsSchema

from django.test import TestCase


class ApiTestCase(TestCase):

    def test_attribution_to_response_returns_response_with_language_as_defined(self):
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
        model = Attribution.objects.create(**model_fields)

        actual = attribution_to_response(model, lang="de")

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

    def test_attribution_to_response_returns_response_with_default_language_if_undefined(self):
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
        model = Attribution.objects.create(**model_fields)

        actual = attribution_to_response(model, lang="it")

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(f"/attributions/{attribution_id}")

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(f"attributions/{attribution_id}?lang=de")

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
        response = client.get("attributions/1")

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(f"attributions/{attribution_id}")

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(f"attributions/{attribution_id}", headers={"Accept-Language": "de"})

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(
            f"attributions/{attribution_id}?lang=fr", headers={"Accept-Language": "de"}
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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(f"attributions/{attribution_id}", headers={"Accept-Language": ""})

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(
            f"attributions/{attribution_id}", headers={"Accept-Language": "cn, *, de-DE, en"}
        )

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get(
            f"attributions/{attribution_id}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
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

    def test_get_attributions_returns_single_attribution_with_given_language(self):

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get("attributions?lang=fr")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "id": f"{attribution_id}",
                "name": "OFEV",
                "name_translations": {
                    "de": "BAFU",
                    "fr": "OFEV",
                    "en": "FOEN",
                    "it": "UFAM",
                    "rm": "UFAM",
                },
                "description": "Office fédéral de l'environnement",
                "description_translations": {
                    "de": "Bundesamt für Umwelt",
                    "fr": "Office fédéral de l'environnement",
                    "en": "Federal Office for the Environment",
                    "it": "Ufficio federale dell'ambiente",
                    "rm": "Uffizi federal per l'ambient",
                },
                "provider_id": str(provider.id),
            }]
        }

    def test_get_attributions_skips_translations_that_are_not_available(self):

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get("attributions")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
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
            }]
        }

    def test_get_attributions_returns_attribution_with_language_from_header(self):

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
        attribution_id = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get("attributions", headers={"Accept-Language": "de"})

        assert response.status_code == 200
        assert response.data == {
            "items": [{
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
            }]
        }

    def test_get_attributions_returns_all_attributions_ordered_by_id_with_given_language(self):

        provider1 = Provider.objects.create()
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
            "provider": provider1,
        }
        attribution_id_1 = Attribution.objects.create(**model_fields).id

        provider2 = Provider.objects.create()
        model_fields = {
            "name_de": "BAV",
            "name_fr": "OFT",
            "name_en": "FOT",
            "name_it": "UFT",
            "name_rm": "UFT",
            "description_de": "Bundesamt für Verkehr",
            "description_fr": "Office fédéral des transports",
            "description_en": "Federal Office of Transport",
            "description_it": "Ufficio federale dei trasporti",
            "description_rm": "Uffizi federal da traffic",
            "provider": provider2,
        }
        attribution_id_2 = Attribution.objects.create(**model_fields).id

        client = TestClient(router)
        response = client.get("attributions?lang=fr")

        assert response.status_code == 200
        assert response.data == {
            "items": [
                {
                    "id": f"{attribution_id_1}",
                    "name": "OFEV",
                    "name_translations": {
                        "de": "BAFU",
                        "fr": "OFEV",
                        "en": "FOEN",
                        "it": "UFAM",
                        "rm": "UFAM",
                    },
                    "description": "Office fédéral de l'environnement",
                    "description_translations": {
                        "de": "Bundesamt für Umwelt",
                        "fr": "Office fédéral de l'environnement",
                        "en": "Federal Office for the Environment",
                        "it": "Ufficio federale dell'ambiente",
                        "rm": "Uffizi federal per l'ambient",
                    },
                    "provider_id": str(provider1.id),
                },
                {
                    "id": f"{attribution_id_2}",
                    "name": "OFT",
                    "name_translations": {
                        "de": "BAV",
                        "fr": "OFT",
                        "en": "FOT",
                        "it": "UFT",
                        "rm": "UFT",
                    },
                    "description": "Office fédéral des transports",
                    "description_translations": {
                        "de": "Bundesamt für Verkehr",
                        "fr": "Office fédéral des transports",
                        "en": "Federal Office of Transport",
                        "it": "Ufficio federale dei trasporti",
                        "rm": "Uffizi federal da traffic",
                    },
                    "provider_id": str(provider2.id),
                },
            ]
        }

    def test_dataset_to_response_returns_response_as_expected(self):
        provider = Provider.objects.create(acronym_de="BAFU")
        attribution = Attribution.objects.create(
            name_de="Kantone",
            provider=provider,
        )
        model_fields = {
            "slug": "ch.bafu.neophyten-haargurke",
            "provider": provider,
            "attribution": attribution,
        }
        time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
            model = Dataset.objects.create(**model_fields)

        actual = dataset_to_response(model)

        assert actual == DatasetSchema(
            id=str(model.id),
            slug="ch.bafu.neophyten-haargurke",
            created=time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated=time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            provider_id=str(provider.id),
            attribution_id=str(attribution.id),
        )

    def test_get_dataset_returns_specified_dataset(self):
        provider = Provider.objects.create(acronym_de="BAFU")
        attribution = Attribution.objects.create(
            name_de="Kantone",
            provider=provider,
        )
        model_fields = {
            "slug": "ch.bafu.neophyten-haargurke",
            "provider": provider,
            "attribution": attribution,
        }
        time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
            dataset = Dataset.objects.create(**model_fields)

        client = TestClient(router)
        response = client.get(f"datasets/{dataset.id}")

        assert response.status_code == 200
        assert response.data == {
            "id": f"{dataset.id}",
            "slug": "ch.bafu.neophyten-haargurke",
            "created": dataset.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated": dataset.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provider_id": str(provider.id),
            "attribution_id": str(provider.id),
        }

    def test_get_datasets_returns_single_dataset_as_expected(self):

        provider = Provider.objects.create(acronym_de="BAFU")
        attribution = Attribution.objects.create(
            name_de="Kantone",
            provider=provider,
        )
        model_fields = {
            "slug": "ch.bafu.neophyten-haargurke",
            "provider": provider,
            "attribution": attribution,
        }
        time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
            dataset = Dataset.objects.create(**model_fields)

        client = TestClient(router)
        response = client.get("datasets")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "id": f"{dataset.id}",
                "slug": "ch.bafu.neophyten-haargurke",
                "created": dataset.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated": dataset.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "provider_id": str(provider.id),
                "attribution_id": str(provider.id),
            }]
        }

    def test_get_datasets_returns_all_datasets_ordered_by_id(self):
        provider1 = Provider.objects.create(acronym_de="Provider1")
        attribution1 = Attribution.objects.create(
            name_de="Attribution1",
            provider=provider1,
        )
        model_fields1 = {
            "slug": "slug1",
            "provider": provider1,
            "attribution": attribution1,
        }
        time_created1 = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created1)):
            dataset1 = Dataset.objects.create(**model_fields1)

        provider2 = Provider.objects.create(acronym_de="Provider2")
        attribution2 = Attribution.objects.create(
            name_de="Attribution2",
            provider=provider2,
        )
        model_fields2 = {
            "slug": "slug2",
            "provider": provider2,
            "attribution": attribution2,
        }
        time_created2 = datetime.datetime(2024, 9, 12, 16, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created1)):
            dataset2 = Dataset.objects.create(**model_fields2)

        client = TestClient(router)
        response = client.get("datasets")

        assert response.status_code == 200
        assert response.data == {
            "items": [
                {
                    "id": f"{dataset1.id}",
                    "slug": "slug1",
                    "created": dataset1.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "updated": dataset1.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "provider_id": str(provider1.id),
                    "attribution_id": str(provider1.id),
                },
                {
                    "id": f"{dataset2.id}",
                    "slug": "slug2",
                    "created": dataset2.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "updated": dataset2.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "provider_id": str(provider2.id),
                    "attribution_id": str(provider2.id),
                },
            ]
        }
