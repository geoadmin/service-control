from difflib import SequenceMatcher
from typing import Any
from typing import Literal
from typing import TypedDict
from typing import cast

from distributions.models import Dataset
from distributions.models import PackageDistribution
from pystac.collection import Collection
from pystac_client import Client
from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management.base import CommandParser
from django.db import transaction

Counter = TypedDict('Counter', {'added': int, 'cleared': int, 'removed': int, 'updated': int})
Operation = Literal['added', 'cleared', 'removed', 'updated']


class Handler(CommandHandler):

    def __init__(self, command: CustomBaseCommand, options: dict['str', Any]):
        super().__init__(command, options)
        self.clear = options['clear']
        self.dry_run = options['dry_run']
        self.similarity = options['similarity']
        self.url = options['url']
        self.counts: dict[str, Counter] = {}

    def increment_counter(self, model_name: str, operation: Operation, value: int = 1) -> None:
        """ Updates internal counters of operations on models. """

        self.counts.setdefault(model_name, {'added': 0, 'cleared': 0, 'removed': 0, 'updated': 0})
        self.counts[model_name][operation] += value

    def clear_package_distributions(self) -> None:
        """ Remove existing package distributions previously imported from STAC. """

        _, cleared = PackageDistribution.objects.filter(managed_by_stac=True).delete()
        for model_class, count in cleared.items():
            model_name = model_class.split('.')[-1].lower()
            self.increment_counter(model_name, 'cleared', count)

    def import_package_distributions(self) -> None:
        """ Import package distributions from STAC.

        This function adds new package distributions, updates existing ones and removes orphans.

        Each STAC collection corresponds to a package distribution (of a dataset with the same
        distribution_id).

        """
        processed = set()

        # Get collections
        client = Client.open(self.url)
        for collection in client.collection_search().collections():
            collection_id = collection.id
            processed.add(collection_id)

            # Get dataset
            dataset = Dataset.objects.filter(dataset_id=collection_id).first()
            if not dataset:
                self.print_warning("No dataset for collection id '%s'", collection_id)
                continue

            # Get or create package distribution
            package_distribution = PackageDistribution.objects.filter(
                package_distribution_id=collection_id
            ).first()
            if not package_distribution:
                package_distribution = PackageDistribution.objects.create(
                    package_distribution_id=collection_id, managed_by_stac=True, dataset=dataset
                )
                self.increment_counter('package_distribution', 'added')
                self.print(f"Added package distribution '{collection_id}'")

            # Update package distribution
            if not package_distribution.managed_by_stac or package_distribution.dataset != dataset:
                package_distribution.managed_by_stac = True
                package_distribution.dataset = dataset
                package_distribution.save()
                self.increment_counter('package_distribution', 'updated')
                self.print(f"Updated package distribution '{collection_id}'")

            self.check_provider(collection, dataset)

        # Remove orphaned package distributions
        orphans = PackageDistribution.objects.filter(managed_by_stac=True).exclude(
            package_distribution_id__in=processed
        )
        _, removed = orphans.delete()
        for model_class, count in removed.items():
            model_name = model_class.split('.')[-1].lower()
            self.increment_counter(model_name, 'removed', count)

    def check_provider(self, collection: Collection, dataset: Dataset) -> None:
        """Checks whether the provider in the STAC collection matches the provider in the dataset
        and warns if they do not.

        A similarity ratio can be applied to minimize warnings for minor textual variations.

        """
        collection_id = collection.id
        providers = collection.providers
        if not providers:
            self.print_warning("Collection '%s' has no providers", collection_id)
        elif len(providers) > 1:
            self.print_warning("Collection '%s' has more than one provider", collection_id)
        else:
            name_collection = providers[0].name
            name_dataset = dataset.provider.name_en
            if name_dataset != name_collection:
                similarity = SequenceMatcher(None, name_collection, name_dataset).ratio()
                if similarity < self.similarity:
                    self.print_warning(
                        "Provider in collection and dataset differ (%.2f): '%s' / '%s'",
                        similarity,
                        name_collection,
                        name_dataset
                    )

    def run(self) -> None:
        """ Main entry point of command. """

        with transaction.atomic():
            # Clear data
            if self.clear:
                self.clear_package_distributions()

            # Import data
            self.import_package_distributions()

            # Print counts
            printed = False
            for model in sorted(self.counts):
                for operation in sorted(self.counts[model]):
                    count = self.counts[model][cast(Operation, operation)]
                    if count:
                        printed = True
                        self.print_success(f"{count} {model}(s) {operation}")
            if not printed:
                self.print_success("nothing to be done, already up to date")

            # Abort if dry run
            if self.dry_run:
                self.print_warning("dry run, aborting transaction")
                transaction.set_rollback(True)


class Command(CustomBaseCommand):
    help = "Harvests data from STAC"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--clear", action="store_true", help="Delete existing objects before importing"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Dry run, abort transaction in the end"
        )
        parser.add_argument(
            "--similarity",
            type=float,
            default=1.0,
            help="Similarity threshold to use when comparing providers"
        )
        parser.add_argument(
            "--url", type=str, default="https://data.geo.admin.ch/api/stac/v0.9", help="STAC URL"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        Handler(self, options).run()
