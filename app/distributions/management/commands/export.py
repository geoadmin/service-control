import json
from typing import Any

import boto3
import environ
from distributions.models import Dataset
from provider.models import Provider
from pydantic import BaseModel
from utils.command import CustomBaseCommand

from django.core import serializers
from django.core.management.base import CommandParser

env = environ.Env()
boto3.setup_default_session(profile_name="swisstopo-swissgeo-dev")

SAMPLE_IDS = [
    "ch.bafu.schutzgebiete-luftfahrt",
    "ch.swisstopo.lubis-luftbilder-dritte-kantone",
    "ch.bav.sachplan-infrastruktur-schiene_anhorung",
    "ch.agroscope.korridore-feuchtgebietsarten_qualitaet",
    "ch.meteoschweiz.messwerte-pollen-buche-1h",
]


class BaseModelWithDynamoDBSerialization(BaseModel):
    """BaseModel with custom serialization for DynamoDB"""

    def as_dynamodb_item(self) -> dict[str, Any]:
        """Convert the dataset to a DynamoDB item format

        Returns:
            dict[str, Any]: The dataset represented as a DynamoDB item.
        """
        item = self.model_dump(mode="json")
        for key, value in item.items():
            if value is None:
                item[key] = {"NULL": True}
            elif isinstance(value, int):
                item[key] = {"N": str(value)}
            elif isinstance(value, str):
                item[key] = {"S": value}
            elif isinstance(value, list) and all(isinstance(i, str) for i in value):
                item[key] = {"L": [{"S": i} for i in value]}
            else:
                raise ValueError(f"Unexpected type {type(value)} for key {key} with value {value}")
        return item


class ExportDataset(BaseModelWithDynamoDBSerialization):
    dataset_id: str
    title_de: str
    title_fr: str
    title_en: str
    title_it: str | None
    title_rm: str | None
    description_de: str
    description_fr: str
    description_en: str
    description_it: str | None
    description_rm: str | None
    attribution: list[str]
    provider: list[str]
    created: str
    updated: str
    geocat_id: str
    _legacy_id: int


class ExportProvider(BaseModelWithDynamoDBSerialization):
    provider_id: str
    created: str
    updated: str
    name_de: str
    name_fr: str
    name_en: str
    name_it: str | None
    name_rm: str | None
    acronym_de: str
    acronym_fr: str
    acronym_en: str
    acronym_it: str | None
    acronym_rm: str | None
    _legacy_id: int


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
