from io import StringIO

from bod.models import BodContactOrganisation
from bod.models import BodDataset
from bod.models import BodGeocatPublish
from bod.models import BodTranslations
from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider
from pytest import fixture

from django.core.management import call_command


@fixture(name="bod_translation")
def fixture_bod_translation(db):
    yield BodTranslations.objects.create(
        msg_id="ch.bafu", de="BAFU", fr="OFEV", en="FOEN", it="UFAM", rm="UFAM"
    )


@fixture(name="bod_contact_organisation")
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
        attribution="ch.bafu",
    )


@fixture(name="bod_dataset")
def fixture_bod_dataset(bod_contact_organisation):
    yield BodDataset.objects.create(
        id=170,
        id_dataset="ch.bafu.auen-vegetationskarten",
        fk_geocat="ab76361f-657d-4705-9053-95f89ecab126",
        fk_contactorganisation_id=bod_contact_organisation.pk_contactorganisation_id,
        staging="prod",
    )


@fixture(name="bod_geocat_publish")
def fixture_bod_geocat_publish(bod_dataset):
    yield BodGeocatPublish.objects.create(
        bgdi_id=170,
        fk_id_dataset="ch.bafu.auen-vegetationskarten",
        bezeichnung_de="vegetationskarten_de",
        bezeichnung_fr="vegetationskarten_fr",
        bezeichnung_it="vegetationskarten_it",
        bezeichnung_rm="vegetationskarten_rm",
        bezeichnung_en="vegetationskarten_en",
        abstract_de="abstract_vegetationskarten_de",
        abstract_fr="abstract_vegetationskarten_fr",
        abstract_it="abstract_vegetationskarten_it",
        abstract_rm="abstract_vegetationskarten_rm",
        abstract_en="abstract_vegetationskarten_en",
    )


@fixture(name="bod_geocat_publish_missing_english")
def fixture_bod_geocat_publish_missing_english(bod_dataset):
    yield BodGeocatPublish.objects.create(
        bgdi_id=170,
        fk_id_dataset="ch.bafu.auen-vegetationskarten",
        bezeichnung_de="vegetationskarten_de",
        bezeichnung_fr="vegetationskarten_fr",
        abstract_de="abstract_vegetationskarten_de",
        abstract_fr="abstract_vegetationskarten_fr",
    )


def test_command_imports(bod_geocat_publish):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "Added provider 'Federal Office for the Environment'" in out.getvalue()
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    provider = Provider.objects.first()
    assert provider.provider_id == "ch.bafu"
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
    assert attribution.attribution_id == "ch.bafu"
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
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
    assert dataset.geocat_id == "ab76361f-657d-4705-9053-95f89ecab126"
    assert dataset.title_de == "vegetationskarten_de"
    assert dataset.title_fr == "vegetationskarten_fr"
    assert dataset.title_it == "vegetationskarten_it"
    assert dataset.title_rm == "vegetationskarten_rm"
    assert dataset.title_en == "vegetationskarten_en"
    assert dataset.description_de == "abstract_vegetationskarten_de"
    assert dataset.description_fr == "abstract_vegetationskarten_fr"
    assert dataset.description_it == "abstract_vegetationskarten_it"
    assert dataset.description_rm == "abstract_vegetationskarten_rm"
    assert dataset.description_en == "abstract_vegetationskarten_en"


def test_command_does_not_need_to_import(db):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "nothing to be done, already in sync" in out.getvalue()


def test_command_no_flag_set(bod_geocat_publish):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=False,
        verbosity=2,
        stdout=out,
    )
    assert "no option provided, nothing changed" in out.getvalue()


def test_command_imports_providers(bod_geocat_publish):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=False,
        datasets=False,
        verbosity=2,
        stdout=out,
    )

    assert "Added provider 'Federal Office for the Environment'" in out.getvalue()
    assert "1 provider(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 0
    assert Dataset.objects.count() == 0

    provider = Provider.objects.first()
    assert provider.provider_id == "ch.bafu"
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


def test_command_skips_invalid_providers(bod_contact_organisation, bod_geocat_publish):
    for attribution in ("somethingelse", "", None):
        bod_contact_organisation.attribution = attribution
        bod_contact_organisation.save()

        out = StringIO()
        call_command(
            "bod_sync",
            providers=True,
            attributions=False,
            datasets=False,
            verbosity=2,
            stdout=out,
        )
        assert "nothing to be done" in out.getvalue()
        assert Provider.objects.count() == 0
        assert Attribution.objects.count() == 0
        assert Dataset.objects.count() == 0


def test_command_imports_attributions(bod_contact_organisation, bod_geocat_publish):
    provider = Provider.objects.create(
        provider_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=True,
        datasets=False,
        verbosity=2,
        stdout=out,
    )
    assert "Added attribution 'ch.bafu'" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 0

    attribution = provider.attribution_set.first()
    assert attribution.attribution_id == "ch.bafu"
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


def test_command_skips_invalid_attributions(
    bod_contact_organisation, bod_geocat_publish
):
    for attribution in (bod_contact_organisation.attribution, "", None):
        bod_contact_organisation.attribution = attribution
        bod_contact_organisation.save()

        out = StringIO()
        call_command(
            "bod_sync",
            providers=False,
            attributions=True,
            datasets=False,
            verbosity=2,
            stdout=out,
        )
        assert (
            f"skipping attribution '{attribution}' as no matching provider was found"
        ) in out.getvalue()
        assert "nothing to be done, already in sync" in out.getvalue()
        assert Provider.objects.count() == 0
        assert Attribution.objects.count() == 0
        assert Dataset.objects.count() == 0


def test_command_imports_datasets(bod_contact_organisation, bod_geocat_publish):
    provider = Provider.objects.create(
        provider_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="BAFU",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "Added dataset 'ch.bafu.auen-vegetationskarten'" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    dataset = provider.dataset_set.first()
    assert dataset.attribution == attribution
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
    assert dataset.geocat_id == "ab76361f-657d-4705-9053-95f89ecab126"
    assert dataset.title_de == "vegetationskarten_de"
    assert dataset.title_fr == "vegetationskarten_fr"
    assert dataset.title_it == "vegetationskarten_it"
    assert dataset.title_rm == "vegetationskarten_rm"
    assert dataset.title_en == "vegetationskarten_en"
    assert dataset.description_de == "abstract_vegetationskarten_de"
    assert dataset.description_fr == "abstract_vegetationskarten_fr"
    assert dataset.description_it == "abstract_vegetationskarten_it"
    assert dataset.description_rm == "abstract_vegetationskarten_rm"
    assert dataset.description_en == "abstract_vegetationskarten_en"


def test_command_imports_datasets_missing_english(
    bod_contact_organisation, bod_geocat_publish_missing_english
):
    provider = Provider.objects.create(
        provider_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="BAFU",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "Added dataset 'ch.bafu.auen-vegetationskarten'" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    dataset = provider.dataset_set.first()
    assert dataset.attribution == attribution
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
    assert dataset.geocat_id == "ab76361f-657d-4705-9053-95f89ecab126"
    assert dataset.title_de == "vegetationskarten_de"
    assert dataset.title_fr == "vegetationskarten_fr"
    assert dataset.title_it is None
    assert dataset.title_rm is None
    assert dataset.title_en == "vegetationskarten_de"
    assert dataset.description_de == "abstract_vegetationskarten_de"
    assert dataset.description_fr == "abstract_vegetationskarten_fr"
    assert dataset.description_it is None
    assert dataset.description_rm is None
    assert dataset.description_en == "abstract_vegetationskarten_de"


def test_command_imports_datasets_missing_geocat(bod_contact_organisation, bod_dataset):
    provider = Provider.objects.create(
        provider_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="BAFU",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "Added dataset 'ch.bafu.auen-vegetationskarten'" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    dataset = provider.dataset_set.first()
    assert dataset.attribution == attribution
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
    assert dataset.geocat_id == "ab76361f-657d-4705-9053-95f89ecab126"
    assert dataset.title_de == "#Missing"
    assert dataset.title_fr == "#Missing"
    assert dataset.title_it is None
    assert dataset.title_rm is None
    assert dataset.title_en == "#Missing"
    assert dataset.description_de == "#Missing"
    assert dataset.description_fr == "#Missing"
    assert dataset.description_it is None
    assert dataset.description_rm is None
    assert dataset.description_en == "#Missing"


def test_command_skips_invalid_datasets(bod_geocat_publish):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert (
        "skipping dataset 'ch.bafu.auen-vegetationskarten' "
        + "as no matching attribution was found"
    ) in out.getvalue()
    assert "nothing to be done, already in sync" in out.getvalue()
    assert Provider.objects.count() == 0
    assert Attribution.objects.count() == 0
    assert Dataset.objects.count() == 0


def test_command_skips_non_prod_datasets(bod_dataset, bod_geocat_publish):
    bod_dataset.staging = "test"

    out = StringIO()
    call_command(
        "bod_sync",
        providers=False,
        attributions=False,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert "nothing to be done, already in sync" in out.getvalue()
    assert Provider.objects.count() == 0
    assert Attribution.objects.count() == 0
    assert Dataset.objects.count() == 0


# pylint: disable=too-many-statements
def test_command_updates(bod_contact_organisation, bod_dataset, bod_geocat_publish):
    # Add objects that will be updated
    provider = Provider.objects.create(
        provider_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="BAFU",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.bafu",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="BAFU",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    dataset = Dataset.objects.create(
        dataset_id="xxx",
        geocat_id="xxx",
        title_de="xxx",
        title_fr="xxx",
        title_en="xxx",
        description_de="xxx",
        description_fr="xxx",
        description_en="xxx",
        provider=provider,
        attribution=attribution,
        _legacy_id=bod_dataset.id,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
    )
    assert f"Changed Provider {provider.id} name_de" in out.getvalue()
    assert f"Changed Provider {provider.id} acronym_de" not in out.getvalue()
    assert "1 provider(s) updated" in out.getvalue()
    assert f"Changed Attribution {attribution.id} name_de" in out.getvalue()
    assert f"Changed Attribution {attribution.id} description_de" not in out.getvalue()
    assert "1 attribution(s) updated" in out.getvalue()
    assert f"Changed Dataset {dataset.id} dataset_id" in out.getvalue()
    assert "1 dataset(s) updated" in out.getvalue()
    assert Provider.objects.count() == 1
    assert Attribution.objects.count() == 1
    assert Dataset.objects.count() == 1

    provider = Provider.objects.first()
    assert provider.provider_id == "ch.bafu"
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
    assert attribution.attribution_id == "ch.bafu"
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
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
    assert dataset.geocat_id == "ab76361f-657d-4705-9053-95f89ecab126"
    assert dataset.title_de == "vegetationskarten_de"
    assert dataset.title_fr == "vegetationskarten_fr"
    assert dataset.title_it == "vegetationskarten_it"
    assert dataset.title_rm == "vegetationskarten_rm"
    assert dataset.title_en == "vegetationskarten_en"
    assert dataset.description_de == "abstract_vegetationskarten_de"
    assert dataset.description_fr == "abstract_vegetationskarten_fr"
    assert dataset.description_it == "abstract_vegetationskarten_it"
    assert dataset.description_rm == "abstract_vegetationskarten_rm"
    assert dataset.description_en == "abstract_vegetationskarten_en"


def test_command_removes_orphaned_provider(bod_geocat_publish):
    # Add objects which will be removed
    provider = Provider.objects.create(
        provider_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=16,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=16,
    )
    Dataset.objects.create(
        dataset_id="xxx",
        geocat_id="xxx",
        title_de="xxx",
        title_fr="xxx",
        title_en="xxx",
        description_de="xxx",
        description_fr="xxx",
        description_en="xxx",
        provider=provider,
        attribution=attribution,
        _legacy_id=160,
    )

    # Add objects which will not be removed
    provider = Provider.objects.create(
        provider_id="ch.yyy",
        name_de="YYY",
        name_fr="YYY",
        name_en="YYY",
        acronym_de="YYYY",
        acronym_fr="YYYY",
        acronym_en="YYYY",
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.yyy",
        name_de="YYYY",
        name_fr="YYYY",
        name_en="YYYY",
        description_de="YYY",
        description_fr="YYY",
        description_en="YYY",
        provider=provider,
    )
    Dataset.objects.create(
        dataset_id="yyyy",
        geocat_id="yyyy",
        title_de="yyyy",
        title_fr="yyyy",
        title_en="yyyy",
        description_de="yyyy",
        description_fr="yyyy",
        description_en="yyyy",
        provider=provider,
        attribution=attribution,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
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
    assert {"BAFU", "YYYY"} == set(
        Provider.objects.values_list("acronym_de", flat=True)
    )
    assert {"BAFU", "YYYY"} == set(
        Attribution.objects.values_list("name_de", flat=True)
    )
    assert {"ch.bafu.auen-vegetationskarten", "yyyy"} == set(
        Dataset.objects.values_list("dataset_id", flat=True)
    )


def test_command_removes_orphaned_attribution(bod_contact_organisation):
    # Add objects which will not be removed
    provider = Provider.objects.create(
        provider_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    # Add objects which will be removed
    attribution = Attribution.objects.create(
        attribution_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=16,
    )
    Dataset.objects.create(
        dataset_id="xxx",
        geocat_id="xxx",
        title_de="xxx",
        title_fr="xxx",
        title_en="xxx",
        description_de="xxx",
        description_fr="xxx",
        description_en="xxx",
        provider=provider,
        attribution=attribution,
        _legacy_id=160,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
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
    assert {"BAFU"} == set(Provider.objects.values_list("acronym_de", flat=True))
    assert {"BAFU"} == set(Attribution.objects.values_list("name_de", flat=True))


def test_command_removes_orphaned_dataset(bod_contact_organisation):
    # Add objects which will not be removed
    provider = Provider.objects.create(
        provider_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
        _legacy_id=bod_contact_organisation.pk_contactorganisation_id,
    )

    # Add objects which will be removed
    Dataset.objects.create(
        dataset_id="xxx",
        geocat_id="xxx",
        title_de="xxx",
        title_fr="xxx",
        title_en="xxx",
        description_de="xxx",
        description_fr="xxx",
        description_en="xxx",
        provider=provider,
        attribution=attribution,
        _legacy_id=160,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        verbosity=2,
        stdout=out,
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
    assert {"BAFU"} == set(Provider.objects.values_list("acronym_de", flat=True))
    assert {"BAFU"} == set(Attribution.objects.values_list("name_de", flat=True))


def test_command_does_not_import_if_dry_run(bod_geocat_publish):
    out = StringIO()
    call_command(
        "bod_sync",
        providers=True,
        attributions=True,
        datasets=True,
        dry_run=True,
        stdout=out,
    )
    assert "1 provider(s) added" in out.getvalue()
    assert "1 attribution(s) added" in out.getvalue()
    assert "1 dataset(s) added" in out.getvalue()
    assert "dry run, aborting" in out.getvalue()
    assert Provider.objects.count() == 0
    assert Attribution.objects.count() == 0
    assert Dataset.objects.count() == 0


def test_command_clears_existing_data(bod_geocat_publish):
    provider = Provider.objects.create(
        provider_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        acronym_de="XXX",
        acronym_fr="XXX",
        acronym_en="XXX",
        _legacy_id=150,
    )
    attribution = Attribution.objects.create(
        attribution_id="ch.xxx",
        name_de="XXX",
        name_fr="XXX",
        name_en="XXX",
        description_de="XXX",
        description_fr="XXX",
        description_en="XXX",
        provider=provider,
    )
    Dataset.objects.create(
        dataset_id="yyyy",
        geocat_id="yyyy",
        title_de="yyyy",
        title_fr="yyyy",
        title_en="yyyy",
        description_de="yyyy",
        description_fr="yyyy",
        description_en="yyyy",
        provider=provider,
        attribution=attribution,
    )

    out = StringIO()
    call_command(
        "bod_sync",
        clear=True,
        providers=True,
        attributions=True,
        datasets=True,
        stdout=out,
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
    assert dataset.dataset_id == "ch.bafu.auen-vegetationskarten"
