from io import StringIO

from bod.models import ContactOrganisation
from provider.models import Provider

from django.core.management import call_command
from django.test import TestCase


class BodMigrateCommandTest(TestCase):

    databases = {'default', 'bod'}

    def setUp(self):
        ContactOrganisation.objects.create(
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
        )

    def test_command_imports_providers(self):
        out = StringIO()
        call_command("bod_migrate", verbose=True, stdout=out)
        self.assertIn("Added provider 'Federal Office for the Environment'", out.getvalue())
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertEqual(Provider.objects.count(), 1)

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

    def test_command_does_not_import_if_dry_run(self):
        out = StringIO()
        call_command("bod_migrate", dry_run=True, stdout=out)
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertIn("dry run, aborting", out.getvalue())
        self.assertEqual(Provider.objects.count(), 0)

    def test_command_clears_existing_data(self):
        Provider.objects.create(
            name_de="XXX",
            name_fr="XXX",
            name_en="XXX",
            acronym_de="XXX",
            acronym_fr="XXX",
            acronym_en="XXX",
        )
        out = StringIO()
        call_command("bod_migrate", clear=True, stdout=out)
        self.assertIn("1 provider(s) deleted", out.getvalue())
        self.assertIn("1 provider(s) added", out.getvalue())
        self.assertEqual(Provider.objects.count(), 1)

        provider = Provider.objects.first()
        self.assertEqual(provider.name_de, "Bundesamt für Umwelt")
