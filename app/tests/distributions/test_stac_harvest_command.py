from io import StringIO
from unittest.mock import patch

from distributions.models import Attribution
from distributions.models import Dataset
from distributions.models import PackageDistribution
from provider.models import Provider
from pystac.collection import Collection
from pystac.provider import Provider as StacProvider
from pytest import fixture

from django.core.management import call_command


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


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_imports(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out

    package_distribution = PackageDistribution.objects.first()
    assert package_distribution.slug == 'ch.bafu.alpweiden-herdenschutzhunde'
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_fails_to_import_if_dataset_is_missing(stac_client, provider, attribution):
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "No dataset for collection id 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert PackageDistribution.objects.count() == 0


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_does_not_need_to_import(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde', managed_by_stac=True, dataset=dataset
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "nothing to be done, already up to date" in out


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_updates(stac_client, provider, attribution):
    dataset_old = Dataset.objects.create(
        slug="ch.bafu.amphibienwanderung-verkehrskonflikte",
        provider=provider,
        attribution=attribution,
    )
    dataset_new = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde', managed_by_stac=False, dataset=dataset_old
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Updated package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "package_distribution(s) updated" in out

    package_distribution = PackageDistribution.objects.first()
    assert package_distribution.slug == 'ch.bafu.alpweiden-herdenschutzhunde'
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset_new


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_removes_orphans(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde.1', managed_by_stac=False, dataset=dataset
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde.2', managed_by_stac=True, dataset=dataset
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = []

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "1 packagedistribution(s) removed" in out

    assert PackageDistribution.objects.count() == 1
    package_distribution = PackageDistribution.objects.first()
    assert package_distribution.slug == 'ch.bafu.alpweiden-herdenschutzhunde.1'


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_clears(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde.1', managed_by_stac=False, dataset=dataset
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde.2', managed_by_stac=True, dataset=dataset
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = []

    out = StringIO()
    call_command("stac_harvest", clear=True, verbosity=2, stdout=out)
    out = out.getvalue()

    assert "1 packagedistribution(s) cleared" in out

    assert PackageDistribution.objects.count() == 1
    assert PackageDistribution.objects.first().slug == 'ch.bafu.alpweiden-herdenschutzhunde.1'


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_runs_dry(stac_client, provider, attribution):
    dataset_old = Dataset.objects.create(
        slug="ch.bafu.amphibienwanderung-verkehrskonflikte",
        provider=provider,
        attribution=attribution,
    )
    dataset_new = Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        slug='ch.bafu.alpweiden-herdenschutzhunde', managed_by_stac=False, dataset=dataset_old
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        ),
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde.1',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", dry_run=True, verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Updated package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "package_distribution(s) updated" in out
    assert "dry run, aborting transaction" in out

    assert PackageDistribution.objects.count() == 1
    package_distribution = PackageDistribution.objects.first()
    assert package_distribution.slug == 'ch.bafu.alpweiden-herdenschutzhunde'
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset_old


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_warns_about_missing_provider(stac_client, provider, attribution):
    Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde', description=None, extent=None, providers=[]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Collection 'ch.bafu.alpweiden-herdenschutzhunde' has no providers" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_warns_about_multiple_providers(stac_client, provider, attribution):
    Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[
                StacProvider(name='Federal Office for the Environment'),
                StacProvider(name='Federal Office for the Environment')
            ]
        ),
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Collection 'ch.bafu.alpweiden-herdenschutzhunde' has more than one provider" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_warns_about_unknown_provider(stac_client, provider, attribution):
    Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office of Culture FOC')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Provider in collection and dataset differ" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_does_not_warn_about_similar_provider(stac_client, provider, attribution):
    Dataset.objects.create(
        slug="ch.bafu.alpweiden-herdenschutzhunde",
        provider=provider,
        attribution=attribution,
    )
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal office for the environment')]
        )
    ]

    out = StringIO()
    call_command("stac_harvest", similarity=0.5, verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Provider in collection and dataset differ" not in out
    assert PackageDistribution.objects.first()
