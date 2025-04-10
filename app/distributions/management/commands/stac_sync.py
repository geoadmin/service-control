from difflib import SequenceMatcher
from re import split
from typing import Any
from typing import Literal
from typing import TypedDict
from typing import cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from distributions.models import Dataset
from distributions.models import PackageDistribution
from pystac.collection import Collection
from pystac_client import Client
from requests import get
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
        self.endpoint = options['endpoint']
        self.default_dataset = options['default_dataset']
        self.counts: dict[str, Counter] = {}

    def increment_counter(self, model_name: str, operation: Operation, value: int = 1) -> None:
        """ Updates internal counters of operations on models. """

        self.counts.setdefault(model_name, {'added': 0, 'cleared': 0, 'removed': 0, 'updated': 0})
        self.counts[model_name][operation] += value

    def clear_package_distributions(self) -> None:
        """ Remove existing package distributions previously imported from STAC. """

        _, cleared = PackageDistribution.objects.filter(_legacy_imported=True).delete()
        for model_class, count in cleared.items():
            model_name = model_class.split('.')[-1].lower()
            self.increment_counter(model_name, 'cleared', count)

    def update_package_distribution(
        self, collection_id: str, managed_by_stac: bool
    ) -> Dataset | None:
        """ Create or update the package distribution with the given ID. """
        managed = 'managed' if managed_by_stac else 'unmanaged'

        # Get dataset
        dataset = (
            Dataset.objects.filter(dataset_id=collection_id).first() or
            Dataset.objects.filter(dataset_id=self.default_dataset).first()
        )
        if not dataset:
            self.print_warning("No dataset for collection id '%s'", collection_id)
            if self.default_dataset:
                self.print_warning("Default dataset '%s' does not exist", self.default_dataset)
            return None

        # Get or create package distribution
        package_distribution = PackageDistribution.objects.filter(
            package_distribution_id=collection_id, _legacy_imported=True
        ).first()
        if not package_distribution:
            package_distribution = PackageDistribution.objects.create(
                package_distribution_id=collection_id,
                _legacy_imported=True,
                managed_by_stac=managed_by_stac,
                dataset=dataset
            )
            self.increment_counter('package_distribution', 'added')
            self.print(f"Added package distribution '{collection_id}' ({managed})")

        # Update package distribution
        if (
            package_distribution.managed_by_stac != managed_by_stac or
            package_distribution.dataset != dataset
        ):
            package_distribution.managed_by_stac = managed_by_stac
            package_distribution.dataset = dataset
            package_distribution.save()
            self.increment_counter('package_distribution', 'updated')
            self.print(f"Updated package distribution '{collection_id}' ({managed})")

        return dataset

    def import_package_distributions(self) -> None:
        """ Import package distributions from STAC.

        This function adds new package distributions, updates existing ones and removes orphans.

        Each STAC collection corresponds to a package distribution (of a dataset with the same
        distribution_id).

        """
        processed = set()

        # Get managed collections from STAC API
        client = Client.open(urljoin(self.url, self.endpoint))
        for collection in client.collection_search().collections():
            collection_id = collection.id
            processed.add(collection_id)

            dataset = self.update_package_distribution(collection_id, True)
            if dataset:
                self.check_provider(collection, dataset)

        # Get unmanaged collections from the HTML root
        response = get(self.url, timeout=60)
        element = BeautifulSoup(response.text, 'html.parser').find('div', id="data")
        if not element:
            raise ValueError(f"Error parsing {self.url}")

        for line in split(r'\r?\n', element.text.strip()):
            line = line.strip()
            if not line:
                continue

            values = line.split(' ')
            if len(values) == 0:
                continue

            collection_id = values[0]
            if collection_id in processed:
                continue

            processed.add(collection_id)

            self.update_package_distribution(collection_id, False)

        # Remove orphaned package distributions
        orphans = PackageDistribution.objects.filter(
            _legacy_imported=True
        ).exclude(package_distribution_id__in=processed,)
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
        parser.add_argument("--url", type=str, default="https://data.geo.admin.ch", help="STAC URL")
        parser.add_argument("--endpoint", type=str, default="/api/stac/v0.9", help="STAC endpoint")
        parser.add_argument(
            "--default-dataset",
            type=str,
            default="",
            help="Add packages with missing dataset to this dataset"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        Handler(self, options).run()
