import json
from cmath import exp
from typing import Any

import boto3
import environ
from bod.models import BodLayersJS
from django.core import serializers
from django.core.management.base import CommandParser
from django.core.serializers.json import DjangoJSONEncoder
from provider.models import Provider
from utils.command import CustomBaseCommand

from distributions.export_models import ExportDataset, ExportLayersJS, ExportProvider
from distributions.models import Dataset

env = environ.Env()
boto3.setup_default_session(profile_name="swisstopo-swissgeo-dev")

SAMPLE_IDS = [
    "ch.bafu.schutzgebiete-luftfahrt",
    "ch.swisstopo.lubis-luftbilder-dritte-kantone",
    "ch.bav.sachplan-infrastruktur-schiene_anhorung",
    "ch.agroscope.korridore-feuchtgebietsarten_qualitaet",
    "ch.meteoschweiz.messwerte-pollen-buche-1h",
]


class PureJSONEncoder(DjangoJSONEncoder):
    def default(self, obj: Any) -> Any:
        print(obj)
        if isinstance(obj, list):
            return [super().default(i) for i in obj]
        return super().default(obj)


class Command(CustomBaseCommand):
    help = "Exports datasets from the system to DynamoDB"

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
            "--sample",
            action="store_true",
            help="Export a sample of datasets (10) instead of all datasets",
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
        parser.add_argument(
            "--layers-js",
            action="store_true",
            help="Import datasets",
        )
        parser.add_argument(
            "--target-env",
            type=str,
            choices=["dev", "int", "prod"],
            default="dev",
            help="Specify the target environment",
        )
        parser.add_argument(
            "--profile-name",
            type=str,
            nargs="?",
            default=None,
            help="Specify the profile name (only needed locally)",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Main entry point of command."""
        if options["profile_name"]:
            self.session = boto3.Session(profile_name=options["profile_name"])  # pylint: disable=attribute-defined-outside-init
        else:
            self.session = boto3.Session()  # pylint: disable=attribute-defined-outside-init

        if options["datasets"]:
            self.export_datasets(*args, **options)
        if options["providers"]:
            self.export_providers(*args, **options)
        if options["layers_js"]:
            self.export_layers_js(*args, **options)

    def export_datasets(self, *args: Any, **options: Any) -> None:

        dynamodb_client = self.session.client("dynamodb", region_name="eu-central-1")

        if options["sample"]:
            self.print("Exporting only a sample of datasets (10)...")
            qs = Dataset.objects.filter(dataset_id__in=SAMPLE_IDS)
        else:
            qs = Dataset.objects.all()
        datasets = json.loads(
            serializers.serialize(
                "json", qs, use_natural_foreign_keys=True, use_natural_primary_keys=True
            )
        )

        for dataset in datasets:
            exp_item = ExportDataset(**dataset["fields"])
            item = exp_item.as_dynamodb_item()
            self.print(f"Exporting dataset {exp_item.dataset_id} to DynamoDB")
            dynamodb_client.put_item(
                TableName=f"harvest-datasets-{options['target_env']}", Item=item
            )

    def export_providers(self, *args: Any, **options: Any) -> None:
        dynamodb_client = self.session.client("dynamodb", region_name="eu-central-1")

        qs = Provider.objects.all()
        providers = json.loads(
            serializers.serialize(
                "json", qs, use_natural_foreign_keys=True, use_natural_primary_keys=True
            )
        )

        for provider in providers:
            exp_item = ExportProvider(**provider["fields"])
            item = exp_item.as_dynamodb_item()
            self.print(f"Exporting provider {exp_item.provider_id} to DynamoDB")
            dynamodb_client.put_item(
                TableName=f"harvest-providers-{options['target_env']}", Item=item
            )

    def export_layers_js(self, *args: Any, **options: Any) -> None:
        dynamodb_client = self.session.client("dynamodb", region_name="eu-central-1")

        qs = BodLayersJS.objects.all().values()

        for layer in qs:
            exp_item = ExportLayersJS(**layer)
            item = exp_item.as_dynamodb_item()
            self.print(
                f"Exporting layers_js for dataset {exp_item.layer_id} to DynamoDB"
            )

            dynamodb_client.put_item(
                TableName=f"harvest-layers-js-{options['target_env']}", Item=item
            )
