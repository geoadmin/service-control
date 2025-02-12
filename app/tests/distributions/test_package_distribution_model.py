from distributions.models import Dataset
from distributions.models import PackageDistribution
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError


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
