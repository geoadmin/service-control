from io import StringIO

from bod.models import BodContactOrganisation
from bod.models import BodDataset
from bod.models import BodTranslations
from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider
from pytest import fixture

from django.core.management import call_command


@fixture(name='bod_translation')
def fixture_bod_translation(db):
    yield BodTranslations.objects.create(
        msg_id="ch.bafu", de="BAFU", fr="OFEV", en="FOEN", it="UFAM", rm="UFAM"
    )


@fixture(name='bod_contact_organisation')
def fixture_bod_contact_organisation(bod_translation):
    yield BodContactOrganisation.objects.create(
        pk_contactorganisation_id=17,
        name_de="Bundesamt für Umwelt",
        name_fr="Office fédéral de l'environnement",
        name_en="Federal Office for the Environment",
        name_it="Ufficio federale dell'ambiente",
        name_rm="Uffizi federal per l'ambient",
        abkuerzung_de="BAFU",
        abkuerzung_fr="OFEV",
        abkuerzung_en="FOEN",
        abkuerzung_it="UFAM",
        abkuerzung_rm="UFAM",
        attribution="ch.bafu"
    )


@fixture(name='bod_dataset')
def fixture_bod_dataset(bod_contact_organisation):
    yield BodDataset.objects.create(
        id=170,
        id_dataset="ch.bafu.auen-vegetationskarten",
        fk_contactorganisation_id=bod_contact_organisation.pk_contactorganisation_id
    )


def test_command_imports(bod_dataset):
    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert "Added provider 'Federal Office for the Environment'" in out.getvalue()
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    provider = Provider.objects.first()
    assert provider.slug == "ch.bafu"
    assert provider.name_de == "Bundesamt für Umwelt"
    assert provider.name_fr == "Office fédéral de l'environnement"
    assert provider.name_en == "Federal Office for the Environment"
    assert provider.name_it == "Ufficio federale dell'ambiente"
    assert provider.name_rm == "Uffizi federal per l'ambient"
    assert provider.acronym_de == "BAFU"
    assert provider.acronym_fr == "OFEV"
    assert provider.acronym_en == "FOEN"
    assert provider.acronym_it == "UFAM"
    assert provider.acronym_rm == "UFAM"

    attribution = provider.attribution_set.first()
    assert attribution.slug == "ch.bafu"
    assert attribution.name_de == "BAFU"
    assert attribution.name_fr == "OFEV"
    assert attribution.name_en == "FOEN"
    assert attribution.name_it == "UFAM"
    assert attribution.name_rm == "UFAM"
    assert attribution.description_de == "BAFU"
    assert attribution.description_fr == "OFEV"
    assert attribution.description_en == "FOEN"
    assert attribution.description_it == "UFAM"
    assert attribution.description_rm == "UFAM"

    dataset = provider.dataset_set.first()
    assert dataset.attribution == attribution
    assert dataset.slug == "ch.bafu.auen-vegetationskarten"


def test_command_does_not_need_to_import(db):
    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert 'nothing to be done, already in sync' in out.getvalue()


def test_command_updates(bod_contact_organisation, bod_dataset):
    # Add objects that will be updated
    provider = Provider.objects.create(
        slug="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id
    )
    attribution = Attribution.objects.create(
        slug="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="BAFU",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id
    )
    dataset = Dataset.objects.create(
        slug="xxx", provider=provider, attribution=attribution, _legacy_id=bod_dataset.id
    )

    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert f"Changed Provider {provider.id} name_de" in out.getvalue()
    assert f"Changed Provider {provider.id} acronym_de" not in out.getvalue()
    assert "1 provider(s) updated" in out.getvalue()
    assert f"Changed Attribution {attribution.id} name_de" in out.getvalue()
    assert f"Changed Attribution {attribution.id} description_de" not in out.getvalue()
    assert "1 attribution(s) updated" in out.getvalue()
    assert f"Changed Dataset {dataset.id} slug" in out.getvalue()
    assert "1 dataset(s) updated" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    provider = Provider.objects.first()
    assert provider.slug == "ch.bafu"
    assert provider.name_de == "Bundesamt für Umwelt"
    assert provider.name_fr == "Office fédéral de l'environnement"
    assert provider.name_en == "Federal Office for the Environment"
    assert provider.name_it == "Ufficio federale dell'ambiente"
    assert provider.name_rm == "Uffizi federal per l'ambient"
    assert provider.acronym_de == "BAFU"
    assert provider.acronym_fr == "OFEV"
    assert provider.acronym_en == "FOEN"
    assert provider.acronym_it == "UFAM"
    assert provider.acronym_rm == "UFAM"

    attribution = provider.attribution_set.first()
    assert attribution.slug == "ch.bafu"
    assert attribution.name_de == "BAFU"
    assert attribution.name_fr == "OFEV"
    assert attribution.name_en == "FOEN"
    assert attribution.name_it == "UFAM"
    assert attribution.name_rm == "UFAM"
    assert attribution.description_de == "BAFU"
    assert attribution.description_fr == "OFEV"
    assert attribution.description_en == "FOEN"
    assert attribution.description_it == "UFAM"
    assert attribution.description_rm == "UFAM"

    dataset = provider.dataset_set.first()
    assert dataset.slug == "ch.bafu.auen-vegetationskarten"


def test_command_removes_orphaned_provider(bod_dataset):
    # Add objects which will be removed
    provider = Provider.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=16
    )
    attribution = Attribution.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=16
    )
    Dataset.objects.create(slug="xxx", provider=provider, attribution=attribution, _legacy_id=160)

    # Add objects which will not be removed
    provider = Provider.objects.create(
        slug="ch.yyy",
        name_de="YYY",
        name_fr="YYY",
        name_en="YYY",
        acronym_de="YYYY",
        acronym_fr="YYYY",
        acronym_en="YYYY",
    )
    attribution = Attribution.objects.create(
        slug="ch.yyy",
        name_de="YYYY",
        name_fr="YYYY",
        name_en="YYYY",
        description_de="YYY",
        description_fr="YYY",
        description_en="YYY",
        provider=provider
    )
    Dataset.objects.create(slug="yyyy", provider=provider, attribution=attribution)

    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert "1 provider(s) removed" in out.getvalue()
    assert "1 attribution(s) removed" in out.getvalue()
    assert "1 dataset(s) removed" in out.getvalue()
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 2
    assert Attribution.objects.count() == 2
    assert Dataset.objects.count() == 2
    assert {'BAFU', 'YYYY'} == set(Provider.objects.values_list('acronym_de', flat=True))
    assert {'BAFU', 'YYYY'} == set(Attribution.objects.values_list('name_de', flat=True))
    assert {'ch.bafu.auen-vegetationskarten',
            'yyyy'} == set(Dataset.objects.values_list('slug', flat=True))


def test_command_removes_orphaned_attribution(bod_contact_organisation):
    # Add objects which will not be removed
    provider = Provider.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id
    )

    # Add objects which will be removed
    attribution = Attribution.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=16
    )
    Dataset.objects.create(slug="xxx", provider=provider, attribution=attribution, _legacy_id=160)

    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert "provider(s) removed" not in out.getvalue()
    assert "1 attribution(s) removed" in out.getvalue()
    assert "1 dataset(s) removed" in out.getvalue()
    assert "provider(s) added" not in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "dataset(s) added" not in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 0
    assert {'BAFU'} == set(Provider.objects.values_list('acronym_de', flat=True))
    assert {'BAFU'} == set(Attribution.objects.values_list('name_de', flat=True))


def test_command_removes_orphaned_dataset(bod_contact_organisation):
    # Add objects which will not be removed
    provider = Provider.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id
    )
    attribution = Attribution.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id
    )

    # Add objects which will be removed
    Dataset.objects.create(slug="xxx", provider=provider, attribution=attribution, _legacy_id=160)

    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, verbosity=2, stdout=out
    )
    assert "provider(s) removed" not in out.getvalue()
    assert "attribution(s) removed" not in out.getvalue()
    assert "1 dataset(s) removed" in out.getvalue()
    assert "provider(s) added" not in out.getvalue()
    assert "attribution(s) added" not in out.getvalue()
    assert "dataset(s) added" not in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 0
    assert {'BAFU'} == set(Provider.objects.values_list('acronym_de', flat=True))
    assert {'BAFU'} == set(Attribution.objects.values_list('name_de', flat=True))


def test_command_does_not_import_if_dry_run(bod_dataset):
    out = StringIO()
    call_command(
        "bod_migrate", providers=True, attributions=True, datasets=True, dry_run=True, stdout=out
    )
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert "dry run, aborting" in out.getvalue()
    assert Provider.objects.count() == 0
    assert Attribution.objects.count() == 0
    assert Dataset.objects.count() == 0


def test_command_clears_existing_data(bod_dataset):
    provider = Provider.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=150
    )
    attribution = Attribution.objects.create(
        slug="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider
    )
    Dataset.objects.create(slug="yyyy", provider=provider, attribution=attribution)

    out = StringIO()
    call_command(
        "bod_migrate", clear=True, providers=True, attributions=True, datasets=True, stdout=out
    )
    assert "1 provider(s) cleared" in out.getvalue()
    assert "1 attribution(s) cleared" in out.getvalue()
    assert "1 dataset(s) cleared" in out.getvalue()
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Dataset.objects.count() == 1

    provider = Provider.objects.first()
    assert provider.name_de == "Bundesamt für Umwelt"

    attribution = provider.attribution_set.first()
    assert attribution.name_de == "BAFU"

    dataset = provider.dataset_set.first()
    assert dataset.slug == "ch.bafu.auen-vegetationskarten"
