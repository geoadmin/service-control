from typing import Any
from typing import Literal
from typing import TypedDict
from typing import cast

from bod.models import BodContactOrganisation
from bod.models import BodDataset
from bod.models import BodGeocatPublish
from bod.models import BodTranslations
from distributions.models import Attribution
from distributions.models import Dataset
from provider.models import Provider
from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management.base import CommandParser
from django.db import transaction

Counter = TypedDict('Counter', {'added': int, 'cleared': int, 'removed': int, 'updated': int})
Operation = Literal['added', 'cleared', 'removed', 'updated']


class Handler(CommandHandler):

    def __init__(self, command: CustomBaseCommand, options: dict['str', Any]):
        super().__init__(command, options)
        self.clear = options["clear"]
        self.dry_run = options["dry_run"]
        self.include_attributions = options["attributions"]
        self.include_providers = options["providers"]
        self.include_datasets = options["datasets"]
        self.counts: dict[str, Counter] = {}

    def increment_counter(self, model_name: str, operation: Operation, value: int = 1) -> None:
        """ Updates internal counters of operations on models. """

        self.counts.setdefault(model_name, {'added': 0, 'cleared': 0, 'removed': 0, 'updated': 0})
        self.counts[model_name][operation] += value

    def update_model(
        self,
        model: Provider | Attribution | Dataset,
        attribute: str,
        new_value: str,
        is_new_model: bool
    ) -> bool:
        """ Update the attributes of the given model and print the changed ones. """

        changed = False
        old_value = getattr(model, attribute)
        if old_value != new_value:
            changed = True
            setattr(model, attribute, new_value)
            if not is_new_model:
                self.print(
                    f"Changed {model.__class__.__name__} {model.id} {attribute} from '{old_value}'"
                    f" to '{new_value}'"
                )
        return changed

    def clear_providers(self) -> None:
        """ Remove existing providers previously imported from BOD. """

        _, cleared = Provider.objects.filter(_legacy_id__isnull=False).delete()
        for model_class, count in cleared.items():
            model_name = model_class.split('.')[-1].lower()
            self.increment_counter(model_name, 'cleared', count)

    def import_providers(self) -> None:
        """ Import providers from the old contact organizations table.

        This function adds new providers, updates existing ones (with a matching legacy ID) and
        removes orphans (with a legacy id not found in the BOD).

        In general, for each entry in the old organizations table the attribution
        value is checked and only those contaning exactly 1 period (e.g. ch.bafu)
        are migrated to the table providers.

        """
        processed = set()

        for organization in BodContactOrganisation.objects.all():
            if not organization.attribution or len(organization.attribution.split('.')) != 2:
                # Skip entries that are not a provider.
                # BodContactOrganisation (table 'contactorganisation') contains providers and
                # attributions. Providers are of the format "ch.<short_name>" and only include a
                # single dot.
                continue

            # Keep track of processed organizations for orphan removal
            legacy_id = organization.pk_contactorganisation_id
            processed.add(legacy_id)

            # Get or create provider
            is_new_model = False
            provider = Provider.objects.filter(_legacy_id=legacy_id).first()
            if not provider:
                is_new_model = True
                provider = Provider.objects.create(
                    _legacy_id=legacy_id,
                    provider_id=organization.attribution,
                    acronym_de="undefined",
                    acronym_fr="undefined",
                    acronym_en="undefined",
                    name_de="undefined",
                    name_fr="undefined",
                    name_en="undefined"
                )
                self.increment_counter('provider', 'added')
                self.print(f"Added provider '{organization.name_en}'")

            self.update_provider(provider, organization, is_new_model)
            provider.save()

        # Remove orphaned providers
        orphans = Provider.objects.filter(_legacy_id__isnull=False
                                         ).exclude(_legacy_id__in=processed)
        _, removed = orphans.delete()
        for model_class, count in removed.items():
            model_name = model_class.split('.')[-1].lower()
            self.increment_counter(model_name, 'removed', count)

    def update_provider(
        self, provider: Provider, organization: BodContactOrganisation, is_new_model: bool
    ) -> None:
        """ Update the attributes of a provider. """

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
            ('provider_id', 'attribution'),
        ):
            changed = self.update_model(
                provider,
                provider_attribute,
                getattr(organization, organization_attribute),
                is_new_model
            )
            any_changed = any_changed or changed
        if any_changed and not is_new_model:
            self.increment_counter('provider', 'updated')

    def import_attribution(self) -> None:
        """ Import the attributions from the old contact organizations table.

        The BOD stores one attribution per organization in a column of the organizations table with
        translations in the translations table. Here, we create one attribution entry for each
        provider or remove additional ones. Each attribution is mapped to a provider by the first
        part of the attribution identifier (e.g. "ch.bafu.kt" maps to "ch.bafu"). These identifiers
        are renamed to attribution_id. The attribution_id of an attribution may be the same as the
        provider_id of its related provider.

        """

        processed = set()

        for organization in BodContactOrganisation.objects.all():

            # Keep track of processed organizations for orphan removal
            legacy_id = organization.pk_contactorganisation_id
            processed.add(legacy_id)

            # Get related provider
            provider = None
            if organization.attribution:
                provider_of_attribution = ".".join(organization.attribution.split(".", 2)[:2])
                provider = Provider.objects.filter(provider_id=provider_of_attribution).first()
            if not provider:
                # Skip as no matching provider
                self.print(
                    f"skipping attribution '{organization.attribution}' " +
                    "as no matching provider was found"
                )
                continue

            # Get or create attribution
            is_new_model = False
            attribution = provider.attribution_set.filter(_legacy_id=legacy_id).first()
            if not attribution:
                is_new_model = True
                attribution = provider.attribution_set.create(
                    _legacy_id=legacy_id,
                    attribution_id=organization.attribution,  # type:ignore[misc]
                    name_de="undefined",
                    name_fr="undefined",
                    name_en="undefined",
                    description_de="undefined",
                    description_fr="undefined",
                    description_en="undefined"
                )
                self.increment_counter('attribution', 'added')
                self.print(f"Added attribution '{organization.attribution}'")

            self.update_attribution(attribution, organization, is_new_model)

            attribution.save()

        # Remove orphaned attributions
        orphans = Attribution.objects.filter(_legacy_id__isnull=False
                                            ).exclude(_legacy_id__in=processed)
        _, removed = orphans.delete()
        for model, count in removed.items():
            model_class = model.split('.')[-1].lower()
            self.increment_counter(model_class, 'removed', count)

    def update_attribution(
        self, attribution: Attribution, organization: BodContactOrganisation, is_new_model: bool
    ) -> None:
        """ Update the attributes of an attribution. """

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
            ('description_rm', 'rm'),
            ('attribution_id', '') # will be updated to organization.attribution
        ):
            changed = self.update_model(
                attribution,
                attribution_attribute,
                getattr(translation, translation_attribute, '') or organization.attribution or
                'undefined',
                is_new_model
            )
            any_changed = any_changed or changed
        if any_changed and not is_new_model:
            self.increment_counter('attribution', 'updated')

    def import_datasets(self) -> None:
        """ Import all datasets of legacy providers.

        This function adds new datasets, updates existing ones (with a matching legacy ID) and
        removes orphans (with a legacy id not found in the BOD).

        In general, each entry in the old datasets table corresponds to one in the new table
        datasets (although with different column names).

        """

        processed = set()
        for bod_dataset in BodDataset.objects.filter(staging='prod').all():
            # Keep track of processed BOD datasets for orphan removal
            legacy_id = bod_dataset.id
            processed.add(legacy_id)

            # Get related attribution and provider
            attribution = Attribution.objects.filter(
                _legacy_id=bod_dataset.fk_contactorganisation_id
            ).first()
            if not attribution:
                # Skip as no matching attribution
                self.print(
                    f"skipping dataset '{bod_dataset.id_dataset}' " +
                    "as no matching attribution was found"
                )
                continue

            if legacy_id in (1485, 1486):
                # Skip datasets ch.swisstopo.konsultation-lk10-flurnamen (1485) and
                # ch.swisstopo.konsultation-lk10-siedlungsnamen (1486) as they have the same
                # geocat_id as ch.swisstopo.landeskarte-farbe-10 (952)
                # geocat_id is cb0f8401-c49a-4bdf-aff6-40a7015ba43a
                self.print(f"skipping dataset '{bod_dataset.id_dataset}'")
                continue

            # Get meta information title and description
            bod_meta = BodGeocatPublish.objects.filter(fk_id_dataset=bod_dataset.id_dataset).first()
            if not bod_meta:
                bod_meta = BodGeocatPublish()

            if not bod_meta.bezeichnung_de:
                bod_meta.bezeichnung_de = "#Missing"
            if not bod_meta.bezeichnung_fr:
                bod_meta.bezeichnung_fr = "#Missing"
            if not bod_meta.abstract_de:
                bod_meta.abstract_de = "#Missing"
            if not bod_meta.abstract_fr:
                bod_meta.abstract_fr = "#Missing"
            # If english is missing, geocat defaults to german translation
            if not bod_meta.bezeichnung_en:
                bod_meta.bezeichnung_en = bod_meta.bezeichnung_de
            if not bod_meta.abstract_en:
                bod_meta.abstract_en = bod_meta.abstract_de

            # Get or create dataset
            is_new_model = False
            dataset = Dataset.objects.filter(
                provider=attribution.provider, attribution=attribution, _legacy_id=legacy_id
            ).first()
            if not dataset:
                is_new_model = True
                dataset = Dataset.objects.create(
                    provider=attribution.provider,
                    attribution=attribution,
                    geocat_id=bod_dataset.fk_geocat,
                    title_de=bod_meta.bezeichnung_de,
                    title_fr=bod_meta.bezeichnung_fr,
                    title_en=bod_meta.bezeichnung_en,
                    title_it=bod_meta.bezeichnung_it,
                    title_rm=bod_meta.bezeichnung_rm,
                    description_de=bod_meta.abstract_de,
                    description_fr=bod_meta.abstract_fr,
                    description_en=bod_meta.abstract_en,
                    description_it=bod_meta.abstract_it,
                    description_rm=bod_meta.abstract_rm,
                    _legacy_id=legacy_id,
                    dataset_id='undefined'
                )
                self.increment_counter('dataset', 'added')
                self.print(f"Added dataset '{bod_dataset.id_dataset}'")

            self.update_dataset(dataset, bod_dataset, bod_meta, is_new_model)

            dataset.save()

        # Remove orphaned datasets
        orphans = Dataset.objects.filter(_legacy_id__isnull=False).exclude(_legacy_id__in=processed)
        _, removed = orphans.delete()
        for model, count in removed.items():
            model_class = model.split('.')[-1].lower()
            self.increment_counter(model_class, 'removed', count)

    def update_dataset(
        self,
        dataset: Dataset,
        bod_dataset: BodDataset,
        bod_meta: BodGeocatPublish,
        is_new_model: bool
    ) -> None:
        """ Update the attributes of a dataset. """

        any_changed = False
        for dataset_attribute, bod_dataset_attribute in (('dataset_id', 'id_dataset'),
            ('geocat_id', 'fk_geocat'),):
            changed = self.update_model(
                dataset,
                dataset_attribute,
                getattr(bod_dataset, bod_dataset_attribute),
                is_new_model
            )
            any_changed = any_changed or changed
        for dataset_attribute, bod_dataset_attribute in (('title_de', 'bezeichnung_de'),
            ('title_fr', 'bezeichnung_fr'),
            ('title_en', 'bezeichnung_en'),
            ('title_it', 'bezeichnung_it'),
            ('title_rm', 'bezeichnung_rm'),
            ('description_de', 'abstract_de'),
            ('description_fr', 'abstract_fr'),
            ('description_en', 'abstract_en'),
            ('description_it', 'abstract_it'),
            ('description_rm', 'abstract_rm'),):
            changed = self.update_model(
                dataset, dataset_attribute, getattr(bod_meta, bod_dataset_attribute), is_new_model
            )
            any_changed = any_changed or changed
        if any_changed and not is_new_model:
            self.increment_counter('dataset', 'updated')

    def run(self) -> None:
        """ Main entry point of command. """

        with transaction.atomic():
            # Clear data
            if self.clear:
                self.clear_providers()
            # Import data
            if self.include_providers:
                self.import_providers()
            if self.include_attributions:
                self.import_attribution()
            if self.include_datasets:
                self.import_datasets()

            # Print counts
            printed = False
            if (
                not self.clear and not self.include_providers and not self.include_attributions and
                not self.include_datasets
            ):
                printed = True
                self.print_warning("no option provided, nothing changed")
            for model in sorted(self.counts):
                for operation in sorted(self.counts[model]):
                    count = self.counts[model][cast(Operation, operation)]
                    if count:
                        printed = True
                        self.print_success(f"{count} {model}(s) {operation}")
            if not printed:
                self.print_success("nothing to be done, already in sync")

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
        parser.add_argument(
            "--providers",
            action="store_true",
            help="Import providers",
        )
        parser.add_argument(
            "--attributions",
            action="store_true",
            help="Import attributions",
        )
        parser.add_argument(
            "--datasets",
            action="store_true",
            help="Import datasets",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        Handler(self, options).run()
