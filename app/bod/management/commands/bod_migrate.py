from bod.models import ContactOrganisation
from provider.models import Provider

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Migrates data from a BOD"

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
            deleted = 0
            added = 0
            updated = 0

            if options["clear"]:
                deleted, _ = Provider.objects.all().delete()

            for organization in ContactOrganisation.objects.all():
                legacy_id = organization.pk_contactorganisation_id
                provider, created = Provider.objects.get_or_create(_legacy_id=legacy_id)
                if created:
                    added += 1
                    if options["verbose"]:
                        self.stdout.write(f"Added provider '{organization.name_en}'")

                changed = False
                for provider_attribute, organization_attribute in (
                    ('name_de', 'name_de'),
                    ('name_de', 'name_de'),
                    ('name_en', 'name_en'),
                    ('name_fr', 'name_fr'),
                    ('name_it', 'name_it'),
                    ('name_rm', 'name_rm'),
                    ('acronym_de', 'abkuerzung_de'),
                    ('acronym_fr', 'abkuerzung_fr'),
                    ('acronym_en', 'abkuerzung_en'),
                    ('acronym_it', 'abkuerzung_it'),
                    ('acronym_rm', 'abkuerzung_rm'),
                ):
                    old = getattr(provider, provider_attribute)
                    new = getattr(organization, organization_attribute)
                    if old != new:
                        changed = True
                        setattr(provider, provider_attribute, new)
                        if options["verbose"] and not created:
                            self.stdout.write(
                                f"Changed provider {provider.id} ({legacy_id}) "
                                f"{provider_attribute} from '{old}' to '{new}'"
                            )
                if changed and not created:
                    updated += 1
                provider.save()

            self.stdout.write(self.style.SUCCESS(f"{deleted} provider(s) deleted"))
            self.stdout.write(self.style.SUCCESS(f"{added} provider(s) added"))
            self.stdout.write(self.style.SUCCESS(f"{updated} provider(s) updated"))

            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("dry run, aborting transaction"))
                transaction.set_rollback(True)
