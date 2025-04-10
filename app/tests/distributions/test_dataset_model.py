import datetime
from unittest import mock

from distributions.models import Dataset
from pytest import raises

from django.core.exceptions import ValidationError


# pylint: disable=too-many-locals
def test_object_created_in_db_with_all_fields_defined(provider, attribution):
    dataset_id = "ch.bafu.neophyten-haargurke"
    geocat_id = "ab76361f-657d-4705-9053-95f89ecab126"
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    title_de = "Invasive gebietsfremde Pflanzen - Potentialkarte Haargurke"
    title_fr = "Plantes exotiques envahissantes - Carte de distribution potentiel Sicyos anguleux"
    title_en = "Invasive alien plants - map of the potential area Sicyos angulatus"
    title_it = "Piante esotiche invasive - carte di distribuzione potenziale Sicios angoloso"
    title_rm = "Plantas exoticas invasivas - Charta da la derasaziun potenziala dal sichius angulus"
    description_de = "Beschreibung Haargurke"
    description_fr = "Description Sicyos anguleux"
    description_en = "Description Sicyos angulatus"
    description_it = "Descrizione Sicios angoloso"
    description_rm = "Descripziun Sicyos angulatus"
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        Dataset.objects.create(
            dataset_id=dataset_id,
            geocat_id=geocat_id,
            title_de=title_de,
            title_fr=title_fr,
            title_en=title_en,
            title_it=title_it,
            title_rm=title_rm,
            description_de=description_de,
            description_fr=description_fr,
            description_en=description_en,
            description_it=description_it,
            description_rm=description_rm,
            provider=provider,
            attribution=attribution,
        )
    datasets = Dataset.objects.all()

    assert len(datasets) == 1

    dataset = Dataset.objects.last()

    assert dataset.dataset_id == dataset_id
    assert dataset.geocat_id == geocat_id
    assert dataset.provider.acronym_de == "BAFU"
    assert dataset.attribution.name_de == "BAFU + Kantone"

    assert dataset.created == time_created
    assert dataset.updated == time_created

    assert dataset.title_de == title_de
    assert dataset.title_fr == title_fr
    assert dataset.title_en == title_en
    assert dataset.title_it == title_it
    assert dataset.title_rm == title_rm
    assert dataset.description_de == description_de
    assert dataset.description_fr == description_fr
    assert dataset.description_en == description_en
    assert dataset.description_it == description_it
    assert dataset.description_rm == description_rm


def test_field_created_matches_creation_time(provider, attribution):
    time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
        dataset = Dataset.objects.create(
            dataset_id='xxxx',
            geocat_id='xxxx',
            title_de="xxxx",
            title_fr="xxxx",
            title_en="xxxx",
            description_de="xxxx",
            description_fr="xxxx",
            description_en="xxxx",
            provider=provider,
            attribution=attribution,
        )
        assert dataset.created == time_created


def test_field_updated_matches_update_time(provider, attribution):
    dataset = Dataset.objects.create(
        dataset_id='xxxx',
        geocat_id='xxxx',
        title_de="xxxx",
        title_fr="xxxx",
        title_en="xxxx",
        description_de="xxxx",
        description_fr="xxxx",
        description_en="xxxx",
        provider=provider,
        attribution=attribution
    )

    time_updated = datetime.datetime(2024, 9, 12, 15, 42, 0, tzinfo=datetime.UTC)
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_updated)):
        dataset.dataset_id = "ch.bafu.neophyten-goetterbaum"
        dataset.save()

    assert dataset.updated == time_updated


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(provider, attribution):
    with raises(ValidationError) as e:
        Dataset.objects.create(provider=provider, attribution=attribution)
