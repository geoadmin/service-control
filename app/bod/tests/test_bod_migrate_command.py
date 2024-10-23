from io import StringIO

from bod.models import BodContactOrganisation
from bod.models import BodDataset
from bod.models import BodTranslations
from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider

from django.core.management import call_command
from django.test import TestCase


class BodMigrateCommandTest(TestCase):

    def setUp(self):
        BodContactOrganisation.objects.create(
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
        BodTranslations.objects.create(
            msg_id="ch.bafu", de="BAFU", fr="OFEV", en="FOEN", it="UFAM", rm="UFAM"
        )
        BodDataset.objects.create(
            id=170, id_dataset="ch.bafu.auen-vegetationskarten", fk_contactorganisation_id=17
        )

    def test_command_imports(self):
        out = StringIO()
        call_command("bod_migrate", verbosity=2, stdout=out)
        self.assertIn("Added provider 'Federal Office for the Environment'", out.getvalue())
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertIn("1 attribution(s) added", out.getvalue())
        self.assertIn("1 dataset(s) added", out.getvalue())
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(Attribution.objects.count(), 1)
        self.assertEqual(Dataset.objects.count(), 1)

        provider = Provider.objects.first()
        self.assertEqual(provider.name_de, "Bundesamt für Umwelt")
        self.assertEqual(provider.name_fr, "Office fédéral de l'environnement")
        self.assertEqual(provider.name_en, "Federal Office for the Environment")
        self.assertEqual(provider.name_it, "Ufficio federale dell'ambiente")
        self.assertEqual(provider.name_rm, "Uffizi federal per l'ambient")
        self.assertEqual(provider.acronym_de, "BAFU")
        self.assertEqual(provider.acronym_fr, "OFEV")
        self.assertEqual(provider.acronym_en, "FOEN")
        self.assertEqual(provider.acronym_it, "UFAM")
        self.assertEqual(provider.acronym_rm, "UFAM")

        attribution = provider.attribution_set.first()
        self.assertEqual(attribution.name_de, "BAFU")
        self.assertEqual(attribution.name_fr, "OFEV")
        self.assertEqual(attribution.name_en, "FOEN")
        self.assertEqual(attribution.name_it, "UFAM")
        self.assertEqual(attribution.name_rm, "UFAM")
        self.assertEqual(attribution.description_de, "BAFU")
        self.assertEqual(attribution.description_fr, "OFEV")
        self.assertEqual(attribution.description_en, "FOEN")
        self.assertEqual(attribution.description_it, "UFAM")
        self.assertEqual(attribution.description_rm, "UFAM")

        dataset = provider.dataset_set.first()
        self.assertEqual(dataset.attribution, attribution)
        self.assertEqual(dataset.slug, "ch.bafu.auen-vegetationskarten")

    def test_command_updates(self):
        provider = Provider.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            acronym_de="BAFU",
            acronym_fr="",
            acronym_en="",
            _legacy_id=17
        )
        attribution = Attribution.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            description_de="BAFU",
            description_fr="",
            description_en="",
            provider=provider,
            _legacy_id=17
        )
        dataset = Dataset.objects.create(
            slug="XXX", provider=provider, attribution=attribution, _legacy_id=170
        )

        out = StringIO()
        call_command("bod_migrate", verbosity=2, stdout=out)
        self.assertIn(f"Changed Provider {provider.id} name_de", out.getvalue())
        self.assertNotIn(f"Changed Provider {provider.id} acronym_de", out.getvalue())
        self.assertIn("1 provider(s) updated", out.getvalue())
        self.assertIn(f"Changed Attribution {attribution.id} name_de", out.getvalue())
        self.assertNotIn(f"Changed Attribution {attribution.id} description_de", out.getvalue())
        self.assertIn("1 attribution(s) updated", out.getvalue())
        self.assertIn(f"Changed Dataset {dataset.id} slug", out.getvalue())
        self.assertIn("1 dataset(s) updated", out.getvalue())
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(Attribution.objects.count(), 1)
        self.assertEqual(Dataset.objects.count(), 1)

        provider = Provider.objects.first()
        self.assertEqual(provider.name_de, "Bundesamt für Umwelt")
        self.assertEqual(provider.name_fr, "Office fédéral de l'environnement")
        self.assertEqual(provider.name_en, "Federal Office for the Environment")
        self.assertEqual(provider.name_it, "Ufficio federale dell'ambiente")
        self.assertEqual(provider.name_rm, "Uffizi federal per l'ambient")
        self.assertEqual(provider.acronym_de, "BAFU")
        self.assertEqual(provider.acronym_fr, "OFEV")
        self.assertEqual(provider.acronym_en, "FOEN")
        self.assertEqual(provider.acronym_it, "UFAM")
        self.assertEqual(provider.acronym_rm, "UFAM")

        attribution = provider.attribution_set.first()
        self.assertEqual(attribution.name_de, "BAFU")
        self.assertEqual(attribution.name_fr, "OFEV")
        self.assertEqual(attribution.name_en, "FOEN")
        self.assertEqual(attribution.name_it, "UFAM")
        self.assertEqual(attribution.name_rm, "UFAM")
        self.assertEqual(attribution.description_de, "BAFU")
        self.assertEqual(attribution.description_fr, "OFEV")
        self.assertEqual(attribution.description_en, "FOEN")
        self.assertEqual(attribution.description_it, "UFAM")
        self.assertEqual(attribution.description_rm, "UFAM")

        dataset = provider.dataset_set.first()
        self.assertEqual(dataset.slug, "ch.bafu.auen-vegetationskarten")

    def test_command_removes_orphaned(self):
        # Add objects which will be removed
        provider = Provider.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            acronym_de="XXX",
            acronym_fr="XXX",
            acronym_en="XXX",
            _legacy_id=16
        )
        attribution = Attribution.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            description_de="XXX",
            description_fr="XXX",
            description_en="XXX",
            provider=provider,
            _legacy_id=16
        )
        Dataset.objects.create(
            slug="XXX", provider=provider, attribution=attribution, _legacy_id=160
        )

        # Add objects which will not be removed
        provider = Provider.objects.create(
            name_de="YYY",
            name_fr="YYY",
            name_en="YYY",
            acronym_de="YYYY",
            acronym_fr="YYYY",
            acronym_en="YYYY",
        )
        attribution = Attribution.objects.create(
            name_de="YYYY",
            name_fr="YYYY",
            name_en="YYYY",
            description_de="YYY",
            description_fr="YYY",
            description_en="YYY",
            provider=provider
        )
        Dataset.objects.create(slug="YYYY", provider=provider, attribution=attribution)

        out = StringIO()
        call_command("bod_migrate", verbosity=2, stdout=out)
        self.assertIn("1 provider(s) removed", out.getvalue())
        self.assertIn("1 attribution(s) removed", out.getvalue())
        self.assertIn("1 dataset(s) removed", out.getvalue())
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertIn("1 attribution(s) added", out.getvalue())
        self.assertIn("1 dataset(s) added", out.getvalue())
        self.assertEqual(Provider.objects.count(), 2)
        self.assertEqual(Attribution.objects.count(), 2)
        self.assertEqual(Dataset.objects.count(), 2)
        self.assertEqual({'BAFU', 'YYYY'},
                         set(Provider.objects.values_list('acronym_de', flat=True)))
        self.assertEqual({'BAFU', 'YYYY'},
                         set(Attribution.objects.values_list('name_de', flat=True)))
        self.assertEqual({'ch.bafu.auen-vegetationskarten', 'YYYY'},
                         set(Dataset.objects.values_list('slug', flat=True)))

    def test_command_does_not_import_if_dry_run(self):
        out = StringIO()
        call_command("bod_migrate", dry_run=True, stdout=out)
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertIn("1 attribution(s) added", out.getvalue())
        self.assertIn("1 dataset(s) added", out.getvalue())
        self.assertIn("dry run, aborting", out.getvalue())
        self.assertEqual(Provider.objects.count(), 0)
        self.assertEqual(Attribution.objects.count(), 0)
        self.assertEqual(Dataset.objects.count(), 0)

    def test_command_clears_existing_data(self):
        provider = Provider.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            acronym_de="XXX",
            acronym_fr="XXX",
            acronym_en="XXX",
            _legacy_id=150
        )
        attribution = Attribution.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            description_de="XXX",
            description_fr="XXX",
            description_en="XXX",
            provider=provider
        )
        Dataset.objects.create(slug="YYYY", provider=provider, attribution=attribution)

        out = StringIO()
        call_command("bod_migrate", clear=True, stdout=out)
        self.assertIn("1 provider(s) cleared", out.getvalue())
        self.assertIn("1 attribution(s) cleared", out.getvalue())
        self.assertIn("1 dataset(s) cleared", out.getvalue())
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertIn("1 attribution(s) added", out.getvalue())
        self.assertIn("1 dataset(s) added", out.getvalue())
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(Dataset.objects.count(), 1)

        provider = Provider.objects.first()
        self.assertEqual(provider.name_de, "Bundesamt für Umwelt")

        attribution = provider.attribution_set.first()
        self.assertEqual(attribution.name_de, "BAFU")

        dataset = provider.dataset_set.first()
        self.assertEqual(dataset.slug, "ch.bafu.auen-vegetationskarten")
