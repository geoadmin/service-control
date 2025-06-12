from io import StringIO
from unittest.mock import patch

from distributions.models import Dataset
from distributions.models import PackageDistribution
from pystac.collection import Collection
from pystac.provider import Provider as StacProvider

from django.core.management import call_command


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_imports(get, stac_client, provider, attribution):
    dataset_1 = Dataset.objects.create(
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
    dataset_2 = Dataset.objects.create(
        dataset_id="ch.bafu.hydrologie-hintergrundkarte",
        geocat_id="bbc6aedb-019f-4a49-8a6c-437264b3bd37",
        title_de="Generalisierte Hintergrundkarte zur Darstellung hydrologischer Daten",
        title_fr="Fond cartographique pour la présentation des données hydrologiques ",
        title_en="Generalised background map for the representation of hydrological data ",
        title_it="Carta base generalizzata per la rappresentazione di dati idrologici ",
        title_rm="",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="",
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
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde' (managed)" in out
    assert "Added package distribution 'ch.bafu.hydrologie-hintergrundkarte' (unmanaged)" in out
    assert "2 package_distribution(s) added" in out

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde'
    )
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset_1

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset_2


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_imports_to_default_dataset(get, stac_client, provider, attribution):
    dataset = Dataset.objects.create(
        dataset_id="default",
        geocat_id="none",
        title_de="default",
        title_fr="default",
        title_en="default",
        title_it="default",
        title_rm="default",
        description_de="default",
        description_fr="default",
        description_en="default",
        description_it="default",
        description_rm="default",
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
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", default_dataset='default', verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde' (managed)" in out
    assert "Added package distribution 'ch.bafu.hydrologie-hintergrundkarte' (unmanaged)" in out
    assert "2 package_distribution(s) added" in out

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde'
    )
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_fails_to_import_if_dataset_is_missing(get, stac_client, provider, attribution):
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "No dataset for collection id 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "No dataset for collection id 'ch.bafu.hydrologie-hintergrundkarte'" in out
    assert PackageDistribution.objects.count() == 0


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_fails_if_default_dataset_is_missing(get, stac_client, provider, attribution):
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command(
        "stac_sync",
        default_dataset='default',
        no_create_default_dataset=True,
        verbosity=2,
        stdout=out
    )
    out = out.getvalue()
    assert "No dataset for collection id 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "No dataset for collection id 'ch.bafu.hydrologie-hintergrundkarte'" in out
    assert "Default dataset 'default' does not exist" in out
    assert PackageDistribution.objects.count() == 0


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_creates_default_dataset(get, stac_client, provider, attribution):
    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", default_dataset='default', verbosity=2, stdout=out)
    out = out.getvalue()

    assert "Added provider 'default' for default dataset" in out
    assert "Added attribution 'default' for default dataset" in out
    assert "Added default dataset 'default'" in out
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde' (managed)" in out
    assert "Added package distribution 'ch.bafu.hydrologie-hintergrundkarte' (unmanaged)" in out
    assert "2 package_distribution(s) added" in out

    default_dataset = Dataset.objects.get(dataset_id='default')
    assert default_dataset.provider.provider_id == 'default'
    assert default_dataset.attribution.attribution_id == 'default'

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde'
    )
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == default_dataset

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == default_dataset


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_does_not_need_to_import(get, stac_client, provider, attribution):
    dataset_1 = Dataset.objects.create(
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
    dataset_2 = Dataset.objects.create(
        dataset_id="ch.bafu.hydrologie-hintergrundkarte",
        geocat_id="bbc6aedb-019f-4a49-8a6c-437264b3bd37",
        title_de="Generalisierte Hintergrundkarte zur Darstellung hydrologischer Daten",
        title_fr="Fond cartographique pour la présentation des données hydrologiques ",
        title_en="Generalised background map for the representation of hydrological data ",
        title_it="Carta base generalizzata per la rappresentazione di dati idrologici ",
        title_rm="",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=True,
        dataset=dataset_1,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte',
        managed_by_stac=False,
        dataset=dataset_2,
        _legacy_imported=True,
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "nothing to be done, already up to date" in out


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_updates(get, stac_client, provider, attribution):
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
    dataset_new_1 = Dataset.objects.create(
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
    dataset_new_2 = Dataset.objects.create(
        dataset_id="ch.bafu.hydrologie-hintergrundkarte",
        geocat_id="bbc6aedb-019f-4a49-8a6c-437264b3bd37",
        title_de="Generalisierte Hintergrundkarte zur Darstellung hydrologischer Daten",
        title_fr="Fond cartographique pour la présentation des données hydrologiques ",
        title_en="Generalised background map for the representation of hydrological data ",
        title_it="Carta base generalizzata per la rappresentazione di dati idrologici ",
        title_rm="",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="",
        provider=provider,
        attribution=attribution,
    )
    dataset_new_3 = Dataset.objects.create(
        dataset_id="default",
        geocat_id="none",
        title_de="default",
        title_fr="default",
        title_en="default",
        title_it="default",
        title_rm="default",
        description_de="default",
        description_fr="default",
        description_en="default",
        description_it="default",
        description_rm="default",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=False,
        dataset=dataset_old,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte',
        managed_by_stac=True,
        dataset=dataset_old,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.laerm-bahnlaerm_tag',
        managed_by_stac=True,
        dataset=dataset_old,
        _legacy_imported=True,
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = """
        <div id="data">
            ch.bafu.hydrologie-hintergrundkarte
            ch.bafu.laerm-bahnlaerm_tag
        </div>
    """

    out = StringIO()
    call_command("stac_sync", default_dataset='default', verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Updated package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "Updated package distribution 'ch.bafu.hydrologie-hintergrundkarte'" in out
    assert "Updated package distribution 'ch.bafu.laerm-bahnlaerm_tag'" in out
    assert "package_distribution(s) updated" in out

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde'
    )
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset_new_1

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset_new_2

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.laerm-bahnlaerm_tag'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset_new_3


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_removes_orphans(get, stac_client, provider, attribution):
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
    dataset_keep_html = Dataset.objects.create(
        dataset_id="keep_html",
        geocat_id="keep_html",
        title_de="keep_html",
        title_fr="keep_html",
        title_en="keep_html",
        description_de="keep_html",
        description_fr="keep_html",
        description_en="keep_html",
        provider=provider,
        attribution=attribution,
    )
    dataset_keep_stac = Dataset.objects.create(
        dataset_id="keep_stac",
        geocat_id="keep_stac",
        title_de="keep_stac",
        title_fr="keep_stac",
        title_en="keep_stac",
        description_de="keep_stac",
        description_fr="keep_stac",
        description_en="keep_stac",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_in_html',
        managed_by_stac=False,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_in_stac',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_dataset_html',
        managed_by_stac=False,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_dataset_stac',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_not_legacy',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=False
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_html',
        managed_by_stac=False,
        dataset=dataset_keep_html,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_stac',
        managed_by_stac=True,
        dataset=dataset_keep_stac,
        _legacy_imported=True
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='remove_missing_dataset_stac',
            description=None,
            extent=None,
            providers=[StacProvider(name='remove_missing_dataset_provider')]
        ),
        Collection(
            id='keep_stac',
            description=None,
            extent=None,
            providers=[StacProvider(name='remove_missing_dataset_provider')]
        )
    ]
    get.return_value.text = '<div id="data">remove_missing_dataset_html\nkeep_html</div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "4 packagedistribution(s) removed" in out

    assert PackageDistribution.objects.count() == 3
    assert {p.package_distribution_id for p in PackageDistribution.objects.all()
           } == {'keep_html', 'keep_stac', 'keep_not_legacy'}


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_removes_orphans_default_datset(get, stac_client, provider, attribution):
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
    dataset_keep_html = Dataset.objects.create(
        dataset_id="keep_html",
        geocat_id="keep_html",
        title_de="keep_html",
        title_fr="keep_html",
        title_en="keep_html",
        description_de="keep_html",
        description_fr="keep_html",
        description_en="keep_html",
        provider=provider,
        attribution=attribution,
    )
    dataset_keep_stac = Dataset.objects.create(
        dataset_id="keep_stac",
        geocat_id="keep_stac",
        title_de="keep_stac",
        title_fr="keep_stac",
        title_en="keep_stac",
        description_de="keep_stac",
        description_fr="keep_stac",
        description_en="keep_stac",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_in_html',
        managed_by_stac=False,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='remove_missing_in_stac',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_missing_dataset_html',
        managed_by_stac=False,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_missing_dataset_stac',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_not_legacy',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=False
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_html',
        managed_by_stac=False,
        dataset=dataset_keep_html,
        _legacy_imported=True
    )
    PackageDistribution.objects.create(
        package_distribution_id='keep_stac',
        managed_by_stac=True,
        dataset=dataset_keep_stac,
        _legacy_imported=True
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='keep_missing_dataset_stac',
            description=None,
            extent=None,
            providers=[StacProvider(name='keep_missing_dataset_provider')]
        ),
        Collection(
            id='keep_stac',
            description=None,
            extent=None,
            providers=[StacProvider(name='keep_missing_dataset_provider')]
        )
    ]
    get.return_value.text = '<div id="data">keep_missing_dataset_html\nkeep_html</div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out, default_dataset=dataset.dataset_id)
    out = out.getvalue()
    assert "2 packagedistribution(s) removed" in out

    assert PackageDistribution.objects.count() == 5
    assert {p.package_distribution_id for p in PackageDistribution.objects.all()} == {
        'keep_html',
        'keep_stac',
        'keep_not_legacy',
        'keep_missing_dataset_html',
        'keep_missing_dataset_stac'
    }


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_clears(get, stac_client, provider, attribution):
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
        dataset=dataset,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.2',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde.3',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=False,
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = []
    get.return_value.text = '<div id="data"></div>'

    out = StringIO()
    call_command("stac_sync", clear=True, verbosity=2, stdout=out)
    out = out.getvalue()

    assert "2 packagedistribution(s) cleared" in out

    assert PackageDistribution.objects.count() == 1
    assert PackageDistribution.objects.first(
    ).package_distribution_id == 'ch.bafu.alpweiden-herdenschutzhunde.3'


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_runs_dry(get, stac_client, provider, attribution):
    dataset = Dataset.objects.create(
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
    Dataset.objects.create(
        dataset_id="ch.bafu.hydrologie-hintergrundkarte",
        geocat_id="bbc6aedb-019f-4a49-8a6c-437264b3bd37",
        title_de="Generalisierte Hintergrundkarte zur Darstellung hydrologischer Daten",
        title_fr="Fond cartographique pour la présentation des données hydrologiques ",
        title_en="Generalised background map for the representation of hydrological data ",
        title_it="Carta base generalizzata per la rappresentazione di dati idrologici ",
        title_rm="",
        description_de="Beschreibung",
        description_fr="Description",
        description_en="Description",
        description_it="Descrizione",
        description_rm="",
        provider=provider,
        attribution=attribution,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde',
        managed_by_stac=False,
        dataset=dataset,
        _legacy_imported=True,
    )
    PackageDistribution.objects.create(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte',
        managed_by_stac=True,
        dataset=dataset,
        _legacy_imported=True,
    )

    stac_client.open.return_value.collection_search.return_value.collections.return_value = [
        Collection(
            id='ch.bafu.alpweiden-herdenschutzhunde',
            description=None,
            extent=None,
            providers=[StacProvider(name='Federal Office for the Environment')]
        )
    ]
    get.return_value.text = '<div id="data">ch.bafu.hydrologie-hintergrundkarte</div>'

    out = StringIO()
    call_command("stac_sync", dry_run=True, verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Updated package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "Updated package distribution 'ch.bafu.hydrologie-hintergrundkarte'" in out
    assert "package_distribution(s) updated" in out
    assert "dry run, aborting transaction" in out

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.alpweiden-herdenschutzhunde'
    )
    assert package_distribution.managed_by_stac is False
    assert package_distribution.dataset == dataset

    package_distribution = PackageDistribution.objects.get(
        package_distribution_id='ch.bafu.hydrologie-hintergrundkarte'
    )
    assert package_distribution.managed_by_stac is True
    assert package_distribution.dataset == dataset


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_warns_about_missing_provider(get, stac_client, provider, attribution):
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
    get.return_value.text = '<div id="data"></div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Collection 'ch.bafu.alpweiden-herdenschutzhunde' has no providers" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_warns_about_multiple_providers(get, stac_client, provider, attribution):
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
    get.return_value.text = '<div id="data"></div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Collection 'ch.bafu.alpweiden-herdenschutzhunde' has more than one provider" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_warns_about_unknown_provider(get, stac_client, provider, attribution):
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
    get.return_value.text = '<div id="data"></div>'

    out = StringIO()
    call_command("stac_sync", verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Provider in collection and dataset differ" in out
    assert PackageDistribution.objects.first()


@patch('distributions.management.commands.stac_sync.Client')
@patch('distributions.management.commands.stac_sync.get')
def test_command_does_not_warn_about_similar_provider(get, stac_client, provider, attribution):
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
    get.return_value.text = '<div id="data"></div>'

    out = StringIO()
    call_command("stac_sync", similarity=0.5, verbosity=2, stdout=out)
    out = out.getvalue()
    assert "Added package distribution 'ch.bafu.alpweiden-herdenschutzhunde'" in out
    assert "1 package_distribution(s) added" in out
    assert "Provider in collection and dataset differ" not in out
    assert PackageDistribution.objects.first()
