import datetime
from unittest import mock

from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider


def test_object_created_in_db_with_all_fields_defined(db):
    slug = "ch.bafu.neophyten-haargurke"
    provider = Provider.objects.create(acronym_de="BAFU")
    attribution = Attribution.objects.create(
        name_de="Kantone",
        provider=provider,
    )
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
    assert dataset.attribution.name_de == "Kantone"

    assert dataset.created == time_created
    assert dataset.updated == time_created


def test_field_created_matches_creation_time(db):
    provider = Provider.objects.create()
    attribution = Attribution.objects.create(provider=provider)

    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        dataset = Dataset.objects.create(
            provider=provider,
            attribution=attribution,
        )
        assert dataset.created == time_created


def test_field_updated_matches_update_time(db):
    provider = Provider.objects.create()
    attribution = Attribution.objects.create(provider=provider)
    dataset = Dataset.objects.create(provider=provider, attribution=attribution)

    time_updated = datetime.datetime(2024, 9, 12, 15, 42, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_updated)):
        dataset.slug = "ch.bafu.neophyten-goetterbaum"
        dataset.save()

    assert dataset.updated == time_updated
