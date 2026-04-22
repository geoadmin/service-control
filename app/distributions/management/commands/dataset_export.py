import json
from typing import TYPE_CHECKING
from typing import Any

import boto3
from distributions.export_models import ExportDataset
from distributions.export_models import ExportProvider
from distributions.models import Dataset
from provider.models import Provider
from utils.command import CustomBaseCommand

from django.core import serializers
from django.core.management.base import CommandParser

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

SAMPLE_IDS = [
    "ch.bafu.schutzgebiete-luftfahrt",
    "ch.swisstopo.lubis-luftbilder-dritte-kantone",
    "ch.bav.sachplan-infrastruktur-schiene_anhorung",
    "ch.agroscope.korridore-feuchtgebietsarten_qualitaet",
    "ch.meteoschweiz.messwerte-pollen-buche-1h",
]


class Command(CustomBaseCommand):
    help = "Exports datasets from the system to DynamoDB"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--sample",
            action="store_true",
            help="Export a sample of datasets (10) instead of all datasets",
        )
        parser.add_argument(
            "--providers",
            action="store_true",
            help="Export providers",
        )
        parser.add_argument(
            "--datasets",
            action="store_true",
            help="Export datasets",
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
            "--table-role-arn",
            type=str,
            nargs="?",
            default=None,
            help="Specify the role ARN to access the harvesting tables in swissgeo accounts",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Main entry point of command."""

        # Show parsed arguments (useful for debugging)
        if options.get("verbosity", 0) >= 2:
            self.print(f"Debug: parsed args = {json.dumps(options)}")

        # Create DynamoDB client
        if options.get("table_role_arn"):
            sts_client = boto3.client("sts")
            assumed_role = sts_client.assume_role(
                RoleArn=options["table_role_arn"],
                RoleSessionName="geocat_harvest",
                DurationSeconds=3600  # 1 hour
            )
            session = boto3.Session(
                aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
                aws_session_token=assumed_role["Credentials"]["SessionToken"]
            )
        elif options.get("profile_name"):
            session = boto3.Session(profile_name=options["profile_name"])
        else:
            session = boto3.Session()

        client = session.client("dynamodb", region_name="eu-central-1")

        if options["datasets"]:
            self.export_datasets(client, options['target_env'], options["sample"])
        if options["providers"]:
            self.export_providers(client, options['target_env'])

    def export_datasets(self, client: "DynamoDBClient", target_env: str, sample: bool) -> None:
        self.print("Fetching existing datasets from DynamoDB")
        obsolete = set()
        paginator = client.get_paginator("scan")
        for page in paginator.paginate(
            TableName=f"harvest-datasets-{target_env}", ProjectionExpression="dataset_id"
        ):
            obsolete.update({item["dataset_id"]["S"] for item in page["Items"]})

        self.print("Exporting datasets to DynamoDB")
        if sample:
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
            client.put_item(TableName=f"harvest-datasets-{target_env}", Item=item)
            obsolete.discard(exp_item.dataset_id)

        self.print("Deleting obsolete datasets")
        for dataset_id in obsolete:
            self.print(f"Deleting dataset {dataset_id} from DynamoDB")
            client.delete_item(
                TableName=f"harvest-datasets-{target_env}", Key={"dataset_id": {
                    "S": dataset_id
                }}
            )

    def export_providers(self, client: "DynamoDBClient", target_env: str) -> None:
        self.print("Fetching existing providers from DynamoDB")
        obsolete = set()
        paginator = client.get_paginator("scan")
        for page in paginator.paginate(
            TableName=f"harvest-providers-{target_env}", ProjectionExpression="provider_id"
        ):
            obsolete.update({item["provider_id"]["S"] for item in page["Items"]})

        self.print("Exporting providers to DynamoDB")
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
            client.put_item(TableName=f"harvest-providers-{target_env}", Item=item)
            obsolete.discard(exp_item.provider_id)

        self.print("Deleting obsolete providers")
        for provider_id in obsolete:
            self.print(f"Deleting provider {provider_id} from DynamoDB")
            client.delete_item(
                TableName=f"harvest-providers-{target_env}",
                Key={"provider_id": {
                    "S": provider_id
                }}
            )
