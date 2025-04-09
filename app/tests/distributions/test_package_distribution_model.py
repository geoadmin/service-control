from distributions.models import Dataset
from distributions.models import PackageDistribution
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError


@fixture(name='dataset')
def fixture_dataset(provider, attribution):
    yield Dataset.objects.create(
        dataset_id="ch.agroscope.feuchtflaechenpotential-kulturlandschaft",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Feuchtflächenpotential Agrarland",
        title_fr="Potentiel des surfaces humides",
        title_en="Wetness potential agricultural land",
        description_de="Feuchtflächenpotential Agrarland",
        description_fr="Potentiel des surfaces humides",
        description_en="Wetness potential agricultural land",
        provider=provider,
        attribution=attribution,
    )


def test_create_package_distribution_in_database(dataset):
    PackageDistribution.objects.create(
        package_distribution_id="ch.agroscope.feuchtflaechenpotential-kulturlandschaft",
        managed_by_stac=True,
        dataset=dataset
    )

    distributions = PackageDistribution.objects.all()

    assert len(distributions) == 1

    distribution = distributions[0]

    assert distribution.package_distribution_id == \
        "ch.agroscope.feuchtflaechenpotential-kulturlandschaft"
    assert distribution.managed_by_stac is True
    assert distribution.dataset == dataset


def test_raises_exception_when_creating_db_object_with_mandatory_field_null(dataset):
    with raises(ValidationError) as e:
        PackageDistribution.objects.create(dataset=dataset)
