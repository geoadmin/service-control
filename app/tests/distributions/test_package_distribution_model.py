from distributions.models import Attribution
from distributions.models import Dataset
from distributions.models import PackageDistribution
from provider.models import Provider
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError


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
def fixture_dataset(provider, attribution):
    yield Dataset.objects.create(
        slug="ch.agroscope.feuchtflaechenpotential-kulturlandschaft",
        provider=provider,
        attribution=attribution,
    )


def test_create_package_distribution_in_database(dataset):
    PackageDistribution.objects.create(
        slug="ch.agroscope.feuchtflaechenpotential-kulturlandschaft",
        managed_by_stac=True,
        dataset=dataset
    )

    distributions = PackageDistribution.objects.all()

    assert len(distributions) == 1

    distribution = distributions[0]

    assert distribution.slug == "ch.agroscope.feuchtflaechenpotential-kulturlandschaft"
    assert distribution.managed_by_stac is True
    assert distribution.dataset == dataset


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(dataset):
    with raises(ValidationError) as e:
        PackageDistribution.objects.create(dataset=dataset)
