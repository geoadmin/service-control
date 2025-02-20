import datetime
from unittest import mock

from distributions.models import Dataset
from pytest import raises

from django.core.exceptions import ValidationError


def test_object_created_in_db_with_all_fields_defined(provider, attribution):
    dataset_id = "ch.bafu.neophyten-haargurke"
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        Dataset.objects.create(
            dataset_id=dataset_id,
            provider=provider,
            attribution=attribution,
        )
    datasets = Dataset.objects.all()

    assert len(datasets) == 1

    dataset = Dataset.objects.last()

    assert dataset.dataset_id == dataset_id
    assert dataset.provider.acronym_de == "BAFU"
    assert dataset.attribution.name_de == "BAFU + Kantone"

    assert dataset.created == time_created
    assert dataset.updated == time_created


def test_field_created_matches_creation_time(provider, attribution):
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        dataset = Dataset.objects.create(
            dataset_id='xxxx',
            provider=provider,
            attribution=attribution,
        )
        assert dataset.created == time_created


def test_field_updated_matches_update_time(provider, attribution):
    dataset = Dataset.objects.create(dataset_id='xxxx', provider=provider, attribution=attribution)

    time_updated = datetime.datetime(2024, 9, 12, 15, 42, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_updated)):
        dataset.dataset_id = "ch.bafu.neophyten-goetterbaum"
        dataset.save()

    assert dataset.updated == time_updated


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(provider, attribution):
    with raises(ValidationError) as e:
        Dataset.objects.create(provider=provider, attribution=attribution)
