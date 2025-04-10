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


@fixture(name='dataset')
def fixture_dataset(attribution, time_created):
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        yield Dataset.objects.create(
            dataset_id="ch.bafu.neophyten-haargurke",
            geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
            title_de="Invasive gebietsfremde Pflanzen - Potentialkarte Haargurke",
            title_fr=
            "Plantes exotiques envahissantes - Carte de distribution potentiel Sicyos anguleux",
            title_en="Invasive alien plants - map of the potential area Sicyos angulatus",
            title_it="Piante esotiche invasive - carte di distribuzione potenziale Sicios angoloso",
            title_rm=
            "Plantas exoticas invasivas - Charta da la derasaziun potenziala dal sichius angulus",
            description_de="Beschreibung Haargurke",
            description_fr="Description Sicyos anguleux",
            description_en="Description Sicyos angulatus",
            description_it="Descrizione Sicios angoloso",
            description_rm="Descripziun Sicyos angulatus",
            provider=attribution.provider,
            attribution=attribution
        )


def test_attribution_to_response_returns_response_with_language_as_defined(attribution):

    actual = attribution_to_response(attribution, lang="de")

    expected = AttributionSchema(
        id="ch.bafu.kt",
        name="BAFU + Kantone",
        name_translations=TranslationsSchema(
            de="BAFU + Kantone",
            fr="OFEV + cantons",
            en="FOEN + cantons",
            it="UFAM + cantoni",
            rm="UFAM + chantuns",
        ),
        description="Bundesamt für Umwelt und Kantone",
        description_translations=TranslationsSchema(
            de="Bundesamt für Umwelt und Kantone",
            fr="Office fédéral de l'environnement et cantons",
            en="Federal Office for the Environment and cantons",
            it="Ufficio federale dell'ambiente e cantoni",
            rm="Uffizi federal per l'ambient e chantuns",
        ),
        provider_id="ch.bafu"
    )

    assert actual == expected


def test_attribution_to_response_returns_response_with_default_language_if_undefined(attribution):

    attribution.name_it = None
    attribution.name_rm = None
    attribution.description_it = None
    attribution.description_rm = None

    actual = attribution_to_response(attribution, lang="it")

    expected = AttributionSchema(
        id="ch.bafu.kt",
        name="FOEN + cantons",
        name_translations=TranslationsSchema(
            de="BAFU + Kantone",
            fr="OFEV + cantons",
            en="FOEN + cantons",
            it=None,
            rm=None,
        ),
        description="Federal Office for the Environment and cantons",
        description_translations=TranslationsSchema(
            de="Bundesamt für Umwelt und Kantone",
            fr="Office fédéral de l'environnement et cantons",
            en="Federal Office for the Environment and cantons",
            it=None,
            rm=None,
        ),
        provider_id="ch.bafu",
    )

    assert actual == expected


def test_get_attribution_returns_existing_attribution_with_default_language(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/attributions/{attribution.attribution_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "FOEN + cantons",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Federal Office for the Environment and cantons",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_language_from_query(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/attributions/{attribution.attribution_id}?lang=de")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "BAFU + Kantone",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Bundesamt für Umwelt und Kantone",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_404_for_nonexisting_attribution(client, django_user_factory):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions/9999")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}


def test_get_attribution_skips_translations_that_are_not_available(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution.name_it = None
    attribution.name_rm = None
    attribution.description_it = None
    attribution.description_rm = None
    attribution.save()

    response = client.get(f"/api/v1/attributions/{attribution.attribution_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "FOEN + cantons",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
        },
        "description": "Federal Office for the Environment and cantons",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_language_from_header(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/attributions/{attribution.attribution_id}", headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "BAFU + Kantone",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Bundesamt für Umwelt und Kantone",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_language_from_query_param_even_if_header_set(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/attributions/{attribution.attribution_id}?lang=fr",
        headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "OFEV + cantons",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Office fédéral de l'environnement et cantons",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_default_language_if_header_empty(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/attributions/{attribution.attribution_id}", headers={"Accept-Language": ""}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "FOEN + cantons",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Federal Office for the Environment and cantons",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_first_known_language_from_header(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/attributions/{attribution.attribution_id}",
        headers={"Accept-Language": "cn, *, de-DE, en"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "BAFU + Kantone",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Bundesamt für Umwelt und Kantone",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_attribution_with_first_language_from_header_ignoring_qfactor(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/attributions/{attribution.attribution_id}",
        headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.kt",
        "name": "OFEV + cantons",
        "name_translations": {
            "de": "BAFU + Kantone",
            "fr": "OFEV + cantons",
            "en": "FOEN + cantons",
            "it": "UFAM + cantoni",
            "rm": "UFAM + chantuns",
        },
        "description": "Office fédéral de l'environnement et cantons",
        "description_translations": {
            "de": "Bundesamt für Umwelt und Kantone",
            "fr": "Office fédéral de l'environnement et cantons",
            "en": "Federal Office for the Environment and cantons",
            "it": "Ufficio federale dell'ambiente e cantoni",
            "rm": "Uffizi federal per l'ambient e chantuns",
        },
        "provider_id": "ch.bafu",
    }


def test_get_attribution_returns_401_if_not_logged_in(attribution, client):

    response = client.get(f"/api/v1/attributions/{attribution.attribution_id}")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_attribution_returns_403_if_no_permission(attribution, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/attributions/{attribution.attribution_id}")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_attributions_returns_single_attribution_with_given_language(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu.kt",
            "name": "OFEV + cantons",
            "name_translations": {
                "de": "BAFU + Kantone",
                "fr": "OFEV + cantons",
                "en": "FOEN + cantons",
                "it": "UFAM + cantoni",
                "rm": "UFAM + chantuns",
            },
            "description": "Office fédéral de l'environnement et cantons",
            "description_translations": {
                "de": "Bundesamt für Umwelt und Kantone",
                "fr": "Office fédéral de l'environnement et cantons",
                "en": "Federal Office for the Environment and cantons",
                "it": "Ufficio federale dell'ambiente e cantoni",
                "rm": "Uffizi federal per l'ambient e chantuns",
            },
            "provider_id": "ch.bafu",
        }]
    }


def test_get_attributions_skips_translations_that_are_not_available(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    attribution.name_it = None
    attribution.name_rm = None
    attribution.description_it = None
    attribution.description_rm = None
    attribution.save()

    response = client.get("/api/v1/attributions")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu.kt",
            "name": "FOEN + cantons",
            "name_translations": {
                "de": "BAFU + Kantone",
                "fr": "OFEV + cantons",
                "en": "FOEN + cantons",
            },
            "description": "Federal Office for the Environment and cantons",
            "description_translations": {
                "de": "Bundesamt für Umwelt und Kantone",
                "fr": "Office fédéral de l'environnement et cantons",
                "en": "Federal Office for the Environment and cantons",
            },
            "provider_id": "ch.bafu",
        }]
    }


def test_get_attributions_returns_attribution_with_language_from_header(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/attributions", headers={"Accept-Language": "de"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu.kt",
            "name": "BAFU + Kantone",
            "name_translations": {
                "de": "BAFU + Kantone",
                "fr": "OFEV + cantons",
                "en": "FOEN + cantons",
                "it": "UFAM + cantoni",
                "rm": "UFAM + chantuns",
            },
            "description": "Bundesamt für Umwelt und Kantone",
            "description_translations": {
                "de": "Bundesamt für Umwelt und Kantone",
                "fr": "Office fédéral de l'environnement et cantons",
                "en": "Federal Office for the Environment and cantons",
                "it": "Ufficio federale dell'ambiente e cantoni",
                "rm": "Uffizi federal per l'ambient e chantuns",
            },
            "provider_id": "ch.bafu",
        }]
    }


def test_get_attributions_returns_all_attributions_ordered_by_id_with_given_language(
    attribution, client, django_user_factory
):
    django_user_factory('test', 'test', [('distributions', 'attribution', 'view_attribution')])
    client.login(username='test', password='test')

    provider2 = Provider.objects.create(
        provider_id="ch.provider2",
        acronym_de="Provider2",
        acronym_fr="Provider2",
        acronym_en="Provider2",
        name_de="Provider2",
        name_fr="Provider2",
        name_en="Provider2"
    )
    model_fields = {
        "attribution_id": "ch.provider2.bav",
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
    Attribution.objects.create(**model_fields)

    response = client.get("/api/v1/attributions?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": "ch.bafu.kt",
                "name": "OFEV + cantons",
                "name_translations": {
                    "de": "BAFU + Kantone",
                    "fr": "OFEV + cantons",
                    "en": "FOEN + cantons",
                    "it": "UFAM + cantoni",
                    "rm": "UFAM + chantuns",
                },
                "description": "Office fédéral de l'environnement et cantons",
                "description_translations": {
                    "de": "Bundesamt für Umwelt und Kantone",
                    "fr": "Office fédéral de l'environnement et cantons",
                    "en": "Federal Office for the Environment and cantons",
                    "it": "Ufficio federale dell'ambiente e cantoni",
                    "rm": "Uffizi federal per l'ambient e chantuns",
                },
                "provider_id": "ch.bafu",
            },
            {
                "id": "ch.provider2.bav",
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
                "provider_id": "ch.provider2",
            },
        ]
    }


def test_get_attributions_returns_401_if_not_logged_in(attribution, client, django_user_factory):
    response = client.get("/api/v1/providers")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_attributions_returns_403_if_no_permission(attribution, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_dataset_returns_specified_dataset(dataset, client, django_user_factory, time_created):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/datasets/{dataset.dataset_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu.neophyten-haargurke",
        "title": "Invasive alien plants - map of the potential area Sicyos angulatus",
        "title_translations": {
            "de": "Invasive gebietsfremde Pflanzen - Potentialkarte Haargurke",
            "fr":
                "Plantes exotiques envahissantes - Carte de distribution potentiel Sicyos anguleux",
            "en": "Invasive alien plants - map of the potential area Sicyos angulatus",
            "it": "Piante esotiche invasive - carte di distribuzione potenziale Sicios angoloso",
            "rm":
                "Plantas exoticas invasivas - Charta da " +
                "la derasaziun potenziala dal sichius angulus",
        },
        "description": "Description Sicyos angulatus",
        "description_translations": {
            "de": "Beschreibung Haargurke",
            "fr": "Description Sicyos anguleux",
            "en": "Description Sicyos angulatus",
            "it": "Descrizione Sicios angoloso",
            "rm": "Descripziun Sicyos angulatus",
        },
        "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provider_id": "ch.bafu",
        "attribution_id": "ch.bafu.kt"
    }


def test_get_dataset_returns_401_if_not_logged_in(dataset, client):
    response = client.get(f"/api/v1/datasets/{dataset.dataset_id}")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_dataset_returns_403_if_no_permission(dataset, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/datasets/{dataset.dataset_id}")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_datasets_returns_single_dataset_as_expected(
    dataset, client, django_user_factory, time_created
):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/datasets")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu.neophyten-haargurke",
            "title": "Invasive alien plants - map of the potential area Sicyos angulatus",
            "title_translations": {
                "de": "Invasive gebietsfremde Pflanzen - Potentialkarte Haargurke",
                "fr":
                    "Plantes exotiques envahissantes - " +
                    "Carte de distribution potentiel Sicyos anguleux",
                "en": "Invasive alien plants - map of the potential area Sicyos angulatus",
                "it":
                    "Piante esotiche invasive - carte " +
                    "di distribuzione potenziale Sicios angoloso",
                "rm":
                    "Plantas exoticas invasivas - Charta " +
                    "da la derasaziun potenziala dal sichius angulus",
            },
            "description": "Description Sicyos angulatus",
            "description_translations": {
                "de": "Beschreibung Haargurke",
                "fr": "Description Sicyos anguleux",
                "en": "Description Sicyos angulatus",
                "it": "Descrizione Sicios angoloso",
                "rm": "Descripziun Sicyos angulatus",
            },
            "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provider_id": "ch.bafu",
            "attribution_id": dataset.attribution.attribution_id,
        }]
    }


def test_get_datasets_returns_all_datasets_ordered_by_dataset_id(
    dataset, client, django_user_factory, time_created
):
    django_user_factory('test', 'test', [('distributions', 'dataset', 'view_dataset')])
    client.login(username='test', password='test')

    provider2 = Provider.objects.create(
        provider_id="ch.provider2",
        acronym_de="Provider2",
        acronym_fr="Provider2",
        acronym_en="Provider2",
        name_de="Provider2",
        name_fr="Provider2",
        name_en="Provider2"
    )
    attribution2 = Attribution.objects.create(
        attribution_id="ch.provider2.attribution2",
        name_de="Attribution2",
        name_fr="Attribution2",
        name_en="Attribution2",
        description_de="Attribution2",
        description_fr="Attribution2",
        description_en="Attribution2",
        provider=provider2,
    )
    model_fields2 = {
        "dataset_id": "ch.provider2.dataset2",
        "geocat_id": "dataset2",
        "title_de": "dataset2",
        "title_fr": "dataset2",
        "title_en": "dataset2",
        "description_de": "dataset2",
        "description_fr": "dataset2",
        "description_en": "dataset2",
        "provider": provider2,
        "attribution": attribution2,
    }
    time_created2 = datetime.datetime(2024, 9, 12, 16, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created2)):
        dataset2 = Dataset.objects.create(**model_fields2)

    response = client.get("/api/v1/datasets")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": "ch.bafu.neophyten-haargurke",
                "title": "Invasive alien plants - map of the potential area Sicyos angulatus",
                "title_translations": {
                    "de": "Invasive gebietsfremde Pflanzen - Potentialkarte Haargurke",
                    "fr":
                        "Plantes exotiques envahissantes - " +
                        "Carte de distribution potentiel Sicyos anguleux",
                    "en": "Invasive alien plants - map of the potential area Sicyos angulatus",
                    "it":
                        "Piante esotiche invasive - carte di" +
                        " distribuzione potenziale Sicios angoloso",
                    "rm":
                        "Plantas exoticas invasivas - Charta " +
                        "da la derasaziun potenziala dal sichius angulus",
                },
                "description": "Description Sicyos angulatus",
                "description_translations": {
                    "de": "Beschreibung Haargurke",
                    "fr": "Description Sicyos anguleux",
                    "en": "Description Sicyos angulatus",
                    "it": "Descrizione Sicios angoloso",
                    "rm": "Descripziun Sicyos angulatus",
                },
                "created": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated": time_created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "provider_id": "ch.bafu",
                "attribution_id": "ch.bafu.kt",
            },
            {
                "id": "ch.provider2.dataset2",
                "title": "dataset2",
                "title_translations": {
                    "de": "dataset2",
                    "fr": "dataset2",
                    "en": "dataset2",
                },
                "description": "dataset2",
                "description_translations": {
                    "de": "dataset2",
                    "fr": "dataset2",
                    "en": "dataset2",
                },
                "created": dataset2.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated": dataset2.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "provider_id": "ch.provider2",
                "attribution_id": "ch.provider2.attribution2",
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
