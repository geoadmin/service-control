from bod.models import BodContactOrganisation
from provider.models import Provider

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Migrates data from a BOD"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

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

    def clear(self):
        cleared, _ = Provider.objects.all().delete()
        if cleared:
            self.messages.append(f"{cleared} provider(s) cleared")

    def import_providers(self, verbose):
        added = 0
        updated = 0
        removed = 0
        processed = set()

        for organization in BodContactOrganisation.objects.all():
            legacy_id = organization.pk_contactorganisation_id
            processed.add(legacy_id)
            provider, created = Provider.objects.get_or_create(_legacy_id=legacy_id)
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
                    if verbose and not created:
                        self.stdout.write(
                            f"Changed provider {provider.id} ({legacy_id}) "
                            f"{provider_attribute} from '{old}' to '{new}'"
                        )
            if changed and not created:
                updated += 1
            if created:
                added += 1
                if verbose:
                    self.stdout.write(f"Added provider '{organization.name_en}'")

            provider.save()

        removed, _ = Provider.objects.filter(_legacy_id__isnull=False).exclude(
            _legacy_id__in=processed).delete()

        if added:
            self.messages.append(f"{added} provider(s) added")
        if updated:
            self.messages.append(f"{updated} provider(s) updated")
        if removed:
            self.messages.append(f"{removed} provider(s) removed")

    def handle(self, *args, **options):
        verbose = "verbose" in options
        with transaction.atomic():
            if options["clear"]:
                self.clear()

            self.import_providers(verbose)

            for message in self.messages:
                self.stdout.write(self.style.SUCCESS(message))
            self.stdout.write(self.style.SUCCESS("Done"))

            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("dry run, aborting transaction"))
                transaction.set_rollback(True)
