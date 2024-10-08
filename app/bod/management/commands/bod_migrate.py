from bod.models import BodContactOrganisation
from bod.models import BodTranslations
from provider.models import Provider
from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management.base import CommandParser
from django.db import transaction


class Handler(CommandHandler):

    def __init__(self, command, options):
        super().__init__(command, options)
        self.clear = options["clear"]
        self.dry_run = options["dry_run"]
        self.counts = {}

    def increment_counter(self, model, operation, value=1):
        """ Updates internal counters of operations on models. """

        self.counts.setdefault(model, {})
        self.counts[model].setdefault(operation, 0)
        self.counts[model][operation] += value

    def update_model(self, model, attribute, new_value, new_model):
        """ Update the given model and print changes. """

        changed = False
        old_value = getattr(model, attribute)
        if old_value != new_value:
            changed = True
            setattr(model, attribute, new_value)
            if not new_model:
                self.print(
                    f"Changed {model.__class__.__name__} {model.id} {attribute} from '{old_value}'"
                    f" to '{new_value}'"
                )
        return changed

    def clear_providers(self):
        """ Remove existing providers previously imported from BOD. """

        _, cleared = Provider.objects.filter(_legacy_id__isnull=False).delete()
        for model, count in cleared.items():
            self.increment_counter(model.split('.')[-1].lower(), 'cleared', count)

    def import_providers(self):
        """ Import providers from the old contact organizations table.

        This function adds new providers, updates existing ones (with a matching legacy ID) and
        removes orphans (with a legacy id not found in the BOD). It also ensures one attribution
        per provider.

        In general, each entry in the old organizations table corresponds to one in the new table
        providers (although with different column names). For attributions, the BOD stores one
        attribution per organization in a column of the organizations table with translations in
        the translations table. Here, we create one attribution entry for each provider or remove
        additional ones.

        """
        processed = set()

        for organization in BodContactOrganisation.objects.all():
            # Keep track of processed organizations for orphan removal
            legacy_id = organization.pk_contactorganisation_id
            processed.add(legacy_id)

            # Get or create provider
            provider, created = Provider.objects.get_or_create(_legacy_id=legacy_id)
            if created:
                self.increment_counter('provider', 'added')
                self.print(f"Added provider '{organization.name_en}'")

            # Update provider attributes
            any_changed = False
            for provider_attribute, organization_attribute in (
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
                changed = self.update_model(
                    provider,
                    provider_attribute,
                    getattr(organization, organization_attribute),
                    created
                )
                any_changed = any_changed or changed
            if any_changed and not created:
                self.increment_counter('provider', 'updated')

            # Save provider
            provider.save()

            # Import attriubtion
            self.import_attribution(provider, organization)

        # Remove orphaned providers
        orphans = Provider.objects.filter(_legacy_id__isnull=False
                                         ).exclude(_legacy_id__in=processed)
        _, removed = orphans.delete()
        for model, count in removed.items():
            self.increment_counter(model.split('.')[-1].lower(), 'removed', count)

    def import_attribution(self, provider, organization):
        # Get or create attribution
        attribution, created = provider.attribution_set.get_or_create()
        if created:
            self.increment_counter('attribution', 'added')
            self.print(f"Added attribution '{organization.attribution}'")

        # Remove additional attributions
        removed, _ = provider.attribution_set.exclude(id=attribution.id).delete()
        self.increment_counter('attribution', 'removed', removed)

        # Update attribution
        any_changed = False
        translation = BodTranslations.objects.filter(msg_id=organization.attribution).first()
        for attribution_attribute, translation_attribute in (
            ('name_de', 'de'),
            ('name_fr', 'fr'),
            ('name_en', 'en'),
            ('name_it', 'it'),
            ('name_rm', 'rm'),
            ('description_de', 'de'),
            ('description_fr', 'fr'),
            ('description_en', 'en'),
            ('description_it', 'it'),
            ('description_rm', 'rm')
        ):
            changed = self.update_model(
                attribution,
                attribution_attribute,
                getattr(translation, translation_attribute, '') or '',
                created
            )
            any_changed = any_changed or changed
        if any_changed and not created:
            self.increment_counter('attribution', 'updated')

        # Save attribution
        attribution.save()

    def run(self):
        """ Main entry point of command. """

        with transaction.atomic():
            # Clear data
            if self.clear:
                self.clear_providers()

            # Import data
            self.import_providers()

            # Print counts
            printed = False
            for model in sorted(self.counts):
                for operation in sorted(self.counts[model]):
                    count = self.counts[model][operation]
                    if count:
                        printed = True
                        self.stdout.write(self.style.SUCCESS(f"{count} {model}(s) {operation}"))
            if not printed:
                self.print_success("nothing to be done")

            # Abort if dry run
            if self.dry_run:
                self.print_warning("dry run, aborting transaction")
                transaction.set_rollback(True)


class Command(CustomBaseCommand):
    help = "Migrates data from a BOD"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
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

    def handle(self, *args, **options):
        Handler(self, options).run()
