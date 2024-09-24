from bod.models import ContactOrganisation
from django.core.management.base import BaseCommand
from django.db import transaction
from provider.models import Provider


class Command(BaseCommand):
    help = "Migrates data from a BOD database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing objects before importing",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run, abort transaction in the end",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show more output",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["clear"]:
                deleted, _ = Provider.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"{deleted} providers deleted"))

            added = 0
            for org in ContactOrganisation.objects.all():
                Provider.objects.create(
                    id=org.pk_contactorganisation_id,
                    name_de=org.name_de,
                    name_en=org.name_en,
                    name_fr=org.name_fr,
                    name_it=org.name_it,
                    name_rm=org.name_rm,
                    acronym_de=org.abkuerzung_de,
                    acronym_fr=org.abkuerzung_fr,
                    acronym_en=org.abkuerzung_en,
                    acronym_it=org.abkuerzung_it,
                    acronym_rm=org.abkuerzung_rm,
                )
                if options["verbose"]:
                    self.stdout.write(f"Added provider '{org.name_en}'")
                added += 1
            self.stdout.write(self.style.SUCCESS(f"{added} providers added"))

            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("dry run, aborting transaction"))
                transaction.set_rollback(True)
