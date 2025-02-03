import datetime
from unittest import mock

from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError


@fixture(name='provider')
def fixture_provider(db):
    yield Provider.objects.create(
        slug="ch.bafu",
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
        slug="ch.bafu",
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


def test_object_created_in_db_with_all_fields_defined(provider, attribution):
    slug = "ch.bafu.neophyten-haargurke"
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        Dataset.objects.create(
            slug=slug,
            provider=provider,
            attribution=attribution,
        )
    datasets = Dataset.objects.all()

    assert len(datasets) == 1

    dataset = Dataset.objects.last()

    assert dataset.slug == slug
    assert dataset.provider.acronym_de == "BAFU"
    assert dataset.attribution.name_de == "BAFU"

    assert dataset.created == time_created
    assert dataset.updated == time_created


def test_field_created_matches_creation_time(provider, attribution):
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        dataset = Dataset.objects.create(
            slug='xxxx',
            provider=provider,
            attribution=attribution,
        )
        assert dataset.created == time_created


def test_field_updated_matches_update_time(provider, attribution):
    dataset = Dataset.objects.create(slug='xxxx', provider=provider, attribution=attribution)

    time_updated = datetime.datetime(2024, 9, 12, 15, 42, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_updated)):
        dataset.slug = "ch.bafu.neophyten-goetterbaum"
        dataset.save()

    assert dataset.updated == time_updated


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(provider, attribution):
    with raises(ValidationError) as e:
        Dataset.objects.create(provider=provider, attribution=attribution)
