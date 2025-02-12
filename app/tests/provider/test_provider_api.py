from provider.api import provider_to_response
from provider.models import Provider
from provider.schemas import ProviderSchema
from schemas import TranslationsSchema


def test_provider_to_response_returns_response_with_language_as_defined(provider):
    actual = provider_to_response(provider, lang="de")

    expected = ProviderSchema(
        id="ch.bafu",
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


def test_provider_to_response_returns_response_with_default_language_if_undefined(provider):
    provider.name_it = None
    provider.name_rm = None
    provider.acronym_it = None
    provider.acronym_rm = None

    actual = provider_to_response(provider, lang="it")

    expected = ProviderSchema(
        id="ch.bafu",
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


def test_get_provider_returns_existing_provider_with_default_language(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/providers/{provider.slug}")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_provider_with_language_from_query(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/providers/{provider.slug}?lang=de")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_404_for_nonexisting_provider(client, django_user_factory):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers/2")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}


def test_get_provider_skips_translations_that_are_not_available(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    provider = Provider.objects.last()
    provider.name_it = None
    provider.name_rm = None
    provider.acronym_it = None
    provider.acronym_rm = None
    provider.save()

    response = client.get(f"/api/v1/providers/{provider.slug}")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_provider_with_language_from_header(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/providers/{provider.slug}", headers={"Accept-Language": "de"})

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_provider_with_language_from_query_param_even_if_header_set(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/providers/{provider.slug}?lang=fr", headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_provider_with_default_language_if_header_empty(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/providers/{provider.slug}", headers={"Accept-Language": ""})

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_provider_with_first_known_language_from_header(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/providers/{provider.slug}", headers={"Accept-Language": "cn, *, de-DE, en"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get(
        f"/api/v1/providers/{provider.slug}", headers={"Accept-Language": "fr;q=0.9, de;q=0.8"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "ch.bafu",
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


def test_get_provider_returns_401_if_not_logged_in(provider, client):
    response = client.get(f"/api/v1/providers/{provider.slug}")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_provider_returns_403_if_no_permission(provider, client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get(f"/api/v1/providers/{provider.slug}")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_providers_returns_single_provider_with_given_language(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu",
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


def test_get_providers_skips_translations_that_are_not_available(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    provider = Provider.objects.last()
    provider.name_it = None
    provider.name_rm = None
    provider.acronym_it = None
    provider.acronym_rm = None
    provider.save()

    response = client.get("/api/v1/providers")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu",
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


def test_get_providers_returns_provider_with_language_from_header(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers", headers={"Accept-Language": "de"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "id": "ch.bafu",
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


def test_get_providers_returns_all_providers_ordered_by_id_with_given_language(
    provider, client, django_user_factory
):
    django_user_factory('test', 'test', [('provider', 'provider', 'view_provider')])
    client.login(username='test', password='test')

    provider = {
        "slug": "ch.bav",
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

    response = client.get("/api/v1/providers?lang=fr")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": "ch.bafu",
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
                "id": "ch.bav",
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


def test_get_providers_returns_401_if_not_logged_in(client):
    response = client.get("/api/v1/providers")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_providers_returns_403_if_no_permission(client, django_user_factory):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/providers")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}
