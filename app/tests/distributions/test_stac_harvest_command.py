from io import StringIO
from unittest.mock import patch

from distributions.models import Dataset
from distributions.models import PackageDistribution
from pystac.collection import Collection
from pystac.provider import Provider as StacProvider

from django.core.management import call_command


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_imports(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
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
    assert package_distribution.package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde'
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
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=True,
        dataset=dataset
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
        dataset_id="ch.bafu.amphibienwanderung-verkehrskonflikte",
        geocat_id="8dc1e2a5-eab0-467a-a570-d994830f8340",
        title_de="Amphibienwanderungen mit Konflikten",
        title_fr="Migration d‘amphibiens - Conflits liés au trafic",
        title_en="Amphibian migration conflicts",
        title_it="Migrazioni di anfibi con conflitti",
        title_rm="Migraziun d'amfibis cun conflicts",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    dataset_new = Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=False,
        dataset=dataset_old
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
    assert package_distribution.package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde'
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset_new


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_removes_orphans(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.1',
        managed_by_stac=False,
        dataset=dataset
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.2',
        managed_by_stac=True,
        dataset=dataset
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = []

    out = StringIO()
    call_command("stac_harvest", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "1 packagedistribution(s) removed" in out

    assert PackageDistribution.objects.count() == 1
    package_distribution = PackageDistribution.objects.first()
    assert package_distribution.package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde.1'


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_clears(stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.1',
        managed_by_stac=False,
        dataset=dataset
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.2',
        managed_by_stac=True,
        dataset=dataset
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = []

    out = StringIO()
    call_command("stac_harvest", clear=True, verbosity=2, stdout=out)
    out = out.getvalue()

    assert "1 packagedistribution(s) cleared" in out

    assert PackageDistribution.objects.count() == 1
    assert PackageDistribution.objects.first(
    ).package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde.1'


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_runs_dry(stac_client, provider, attribution):
    dataset_old = Dataset.objects.create(
        dataset_id="ch.bafu.amphibienwanderung-verkehrskonflikte",
        geocat_id="8dc1e2a5-eab0-467a-a570-d994830f8340",
        title_de="Amphibienwanderungen mit Konflikten",
        title_fr="Migration d'amphibiens - Conflits liés au trafic",
        title_en="Amphibian migration conflicts",
        title_it="Migrazioni di anfibi con conflitti",
        title_rm="Migraziun d'amfibis cun conflicts",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    dataset_new = Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=False,
        dataset=dataset_old
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
    assert package_distribution.package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde'
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset_old


@patch('distributions.management.commands.stac_harvest.Client')
def test_command_warns_about_missing_provider(stac_client, provider, attribution):
    Dataset.objects.create(
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
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
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
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
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
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
        dataset_id="ch.bafu.alpweiden-herdenschutzhunde",
        geocat_id="ab76361f-657d-4705-9053-95f89ecab126",
        title_de="Alpweiden mit Herdenschutzhunden",
        title_fr="Alpages protégés par des chiens",
        title_en="Alps with livestock guardian dogs",
        title_it="Alpeggi con cani da guardiania",
        title_rm="Pastgiras d'alp cun chauns prot.",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="Descripziun",
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
