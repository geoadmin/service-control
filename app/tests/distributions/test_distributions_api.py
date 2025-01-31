import datetime
from unittest import mock

from distributions.api import attribution_to_response
from distributions.models import Attribution
from distributions.models import Dataset
from distributions.schemas import AttributionSchema
from provider.models import Provider
from pytest import fixture
from schemas import TranslationsSchema


@fixture(name='time_created')
def fixture_time_created():
    yield datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)


@fixture(name='provider')
def fixture_provider(db):
    yield Provider.objects.create(
        acronym_de="BAFU",
        acronym_fr="OFEV",
        acronym_en="FOEN",
        name_de="Bundesamt für Umwelt",
        name_fr="Office fédéral de l'environnement",
        name_en="Federal Office for the Environment"
    )


@fixture(name='attribution')
def fixture_attribution(provider):
    yield Attribution.objects.create(
        name_de="BAFU",
        name_fr="OFEV",
        name_en="FOEN",
        name_it="UFAM",
        name_rm="UFAM",
        description_de="Bundesamt für Umwelt",
        description_fr="Office fédéral de l'environnement",
        description_en="Federal Office for the Environment",
        description_it="Ufficio federale dell'ambiente",
        description_rm="Uffizi federal per l'ambient",
        provider=provider
    )


@fixture(name='dataset')
def fixture_dataset(provider, attribution, time_created):
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        yield Dataset.objects.create(
            slug="ch.bafu.neophyten-haargurke", provider=provider, attribution=attribution
        )


def test_attribution_to_response_returns_response_with_language_as_defined(dataset):

    model = Attribution.objects.last()
    actual = attribution_to_response(model, lang="de")

    expected = AttributionSchema(
        id=model.id,
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
        provider_id=Provider.objects.last().id
    )

    assert actual == expected


def test_attribution_to_response_returns_response_with_default_language_if_undefined(dataset):

    model = Attribution.objects.last()
    model.name_it = None
    model.name_rm = None
    model.description_it = None
    model.description_rm = None

    actual = attribution_to_response(model, lang="it")

    expected = AttributionSchema(
        id=model.id,
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
        provider_id=Provider.objects.last().id,
    )

    assert actual == expected


def test_get_attribution_returns_existing_attribution_with_default_language(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(f"/api/v1/attributions/{attribution_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_language_from_query(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(f"/api/v1/attributions/{attribution_id}?lang=de")

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_404_for_nonexisting_attribution(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions/9999")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}


def test_get_attribution_skips_translations_that_are_not_available(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    model = Attribution.objects.last()
    model.name_it = None
    model.name_rm = None
    model.description_it = None
    model.description_rm = None
    model.save()

    response = client.get(f"/api/v1/attributions/{model.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": model.id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_language_from_header(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(
        f"/api/v1/attributions/{attribution_id}", headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_language_from_query_param_even_if_header_set(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(
        f"/api/v1/attributions/{attribution_id}?lang=fr", headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_default_language_if_header_empty(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(f"/api/v1/attributions/{attribution_id}", headers={"Accept-Language": ""})

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_first_known_language_from_header(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(
        f"/api/v1/attributions/{attribution_id}", headers={"Accept-Language": "cn, *, de-DE, en"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_attribution_with_first_language_from_header_ignoring_qfactor(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id

    response = client.get(
        f"/api/v1/attributions/{attribution_id}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribution_id,
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
        "provider_id": Provider.objects.last().id,
    }


def test_get_attribution_returns_401_if_not_logged_in(dataset, client):
    attribution_id = Attribution.objects.last().id
    response = client.get(f"/api/v1/attributions/{attribution_id}")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_attribution_returns_403_if_no_permission(dataset, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    attribution_id = Attribution.objects.last().id
    response = client.get(f"/api/v1/attributions/{attribution_id}")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_attributions_returns_single_attribution_with_given_language(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": Attribution.objects.last().id,
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
            "provider_id": Provider.objects.last().id,
        }]
    }


def test_get_attributions_skips_translations_that_are_not_available(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    model = Attribution.objects.last()
    model.name_it = None
    model.name_rm = None
    model.description_it = None
    model.description_rm = None
    model.save()

    response = client.get("/api/v1/attributions")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": Attribution.objects.last().id,
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
            "provider_id": Provider.objects.last().id,
        }]
    }


def test_get_attributions_returns_attribution_with_language_from_header(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions", headers={"Accept-Language": "de"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": Attribution.objects.last().id,
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
            "provider_id": Provider.objects.last().id,
        }]
    }


def test_get_attributions_returns_all_attributions_ordered_by_id_with_given_language(
    dataset, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    provider1 = Provider.objects.last()
    attribution_id_1 = Attribution.objects.last().id

    provider2 = Provider.objects.create(
        acronym_de="Provider2",
        acronym_fr="Provider2",
        acronym_en="Provider2",
        name_de="Provider2",
        name_fr="Provider2",
        name_en="Provider2"
    )
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

    response = client.get("/api/v1/attributions?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": attribution_id_1,
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
                "provider_id": provider1.id,
            },
            {
                "id": attribution_id_2,
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
                "provider_id": provider2.id,
            },
        ]
    }


def test_get_attributions_returns_401_if_not_logged_in(dataset, client, django_user_factory):
    response = client.get("/api/v1/providers")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_attributions_returns_403_if_no_permission(dataset, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_dataset_returns_specified_dataset(dataset, client, django_user_factory, time_created):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    dataset_id = Dataset.objects.last().id

    response = client.get(f"/api/v1/datasets/{dataset_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": dataset_id,
        "slug": "ch.bafu.neophyten-haargurke",
        "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provider_id": Provider.objects.last().id,
        "attribution_id": Attribution.objects.last().id,
    }


def test_get_dataset_returns_401_if_not_logged_in(dataset, client):
    dataset_id = Dataset.objects.last().id
    response = client.get(f"/api/v1/datasets/{dataset_id}")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_dataset_returns_403_if_no_permission(dataset, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    dataset_id = Dataset.objects.last().id
    response = client.get(f"/api/v1/datasets/{dataset_id}")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_datasets_returns_single_dataset_as_expected(
    dataset, client, django_user_factory, time_created
):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/datasets")

    dataset = Dataset.objects.last()
    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": dataset.id,
            "slug": "ch.bafu.neophyten-haargurke",
            "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provider_id": Provider.objects.last().id,
            "attribution_id": Attribution.objects.last().id,
        }]
    }


def test_get_datasets_returns_all_datasets_ordered_by_id(
    dataset, client, django_user_factory, time_created
):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    provider2 = Provider.objects.create(
        acronym_de="Provider2",
        acronym_fr="Provider2",
        acronym_en="Provider2",
        name_de="Provider2",
        name_fr="Provider2",
        name_en="Provider2"
    )
    attribution2 = Attribution.objects.create(
        name_de="Attribution2",
        name_fr="Attribution2",
        name_en="Attribution2",
        description_de="Attribution2",
        description_fr="Attribution2",
        description_en="Attribution2",
        provider=provider2,
    )
    model_fields2 = {
        "slug": "slug2",
        "provider": provider2,
        "attribution": attribution2,
    }
    time_created2 = datetime.datetime(2024, 9, 12, 16, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created2)):
        dataset2 = Dataset.objects.create(**model_fields2)

    response = client.get("/api/v1/datasets")

    dataset1 = Dataset.objects.first()
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": dataset1.id,
                "slug": dataset1.slug,
                "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "provider_id": Provider.objects.first().id,
                "attribution_id": Attribution.objects.first().id,
            },
            {
                "id": dataset2.id,
                "slug": "slug2",
                "created": dataset2.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated": dataset2.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "provider_id": provider2.id,
                "attribution_id": attribution2.id,
            },
        ]
    }


def test_get_datasets_returns_401_if_not_logged_in(dataset, client):
    response = client.get("/api/v1/datasets")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_datasets_returns_403_if_no_permission(dataset, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/datasets")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}
