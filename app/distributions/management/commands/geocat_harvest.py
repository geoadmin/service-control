import json
from functools import cache
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

import boto3
from bod.models import BodDataset
from boto3 import Session
from distributions.export_models import Contact
from distributions.export_models import ContactList
from distributions.export_models import Keyword
from distributions.export_models import KeywordList
from distributions.export_models import OnlineResource
from lxml import etree
from rdflib import Graph
from rdflib import Literal
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from requests import get
from utils.command import CustomBaseCommand

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

    from django.core.management.base import CommandParser

GEOCAT_URL = "https://www.geocat.ch/geonetwork/srv/api/records/{}/formatters/xml?approved=true"
NS = {
    "che": "http://www.geocat.ch/2008/che",
    "gco": "http://www.isotc211.org/2005/gco",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gmx": "http://www.isotc211.org/2005/gmx",
    "xlink": "http://www.w3.org/1999/xlink",
}
TIMEOUT = 30


class Thesaurus:
    """Stores thesaurus concepts and their translations and allows lookup of concepts by any
    translation.

    Keywords in geocat are defined using a thesaurus but are stored as freetext property, i.e.
    a text with optional translations but without the identifier of the underlying concept.
    Since the text usually is equal to one of the translations, it should be possible to make a
    reverse lookup using the thesaurus to fill in the identifier and the missing translations.
    """

    def __init__(self) -> None:
        self.concepts: dict[str, dict[str, str]] = {}
        self.index: dict[str, dict[str, str]] = {}

    def build(self, url: str) -> bool:
        """Build the thesaurus by creating a list of concepts with its translations and a lookup
        table for each translation.

        The thesaurus is defined as RDF (Resource Description Framework), a directed graph of
        triples (subject, predicate, object). Each concept is represented by two kinds of triples:
        a type triple (concept URI, rdf:type, skos:Concept) and one label triple per language
        (concept URI, skos:prefLabel, translation).

        We first collect all known concept URIs from the type triples, then iterate over all
        triples to find prefLabel entries for all the concepts and supported languages.
        """
        if not url:
            return False

        response = get(url, timeout=TIMEOUT, headers={"Accept": "text/xml"})
        if response.status_code != HTTPStatus.OK:
            return False

        graph = Graph()
        graph.parse(data=response.content, format="xml")

        concepts = list(graph.subjects(RDF.type, SKOS.Concept))

        for subject, predicate, label in graph:
            if (
                subject in concepts and predicate == SKOS.prefLabel and
                isinstance(label, Literal) and label.language in ('de', 'fr', 'en', 'it', 'rm')
            ):
                self.concepts.setdefault(str(subject), {})[label.language] = str(label)
                self.index.setdefault(label.language, {})[str(label)] = str(subject)

        return True

    def find_concept(self, term: str) -> tuple[str | None, dict[str, str]]:
        """Find a concept by translation.

        Try to find a concept by searching all translations for the given term.
        """

        for lang in ('de', 'fr', 'en', 'it', 'rm'):
            if concept := self.index.get(lang, {}).get(term):
                return concept, self.concepts[concept]
        return None, {}

    @staticmethod
    @cache
    def get(url: str) -> "Thesaurus | None":
        result = Thesaurus()
        return result if result.build(url) else None


class Command(CustomBaseCommand):
    """Harvest data from geocat and store them in DynamoDB harvesting tables.

    This command retrieves data from geocat metadata entries and exports them to DynamoDB
    harvesting tables. Currently supports only dataset keywords and contact information.

    """

    help = "Harvest geocat metadata and save them to DynamoDB harvesting tables."

    def add_arguments(self, parser: "CommandParser") -> None:
        super().add_arguments(parser)

        parser.add_argument(
            "--harvest-keywords",
            action="store_true",
            help="Harvest keywords of the available datasets",
        )
        parser.add_argument(
            "--harvest-contacts",
            action="store_true",
            help="Harvest contact information of the available datasets",
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
            session = Session(
                aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
                aws_session_token=assumed_role["Credentials"]["SessionToken"]
            )
        elif options.get("profile_name"):
            session = Session(profile_name=options["profile_name"])
        else:
            session = Session()

        client = session.client("dynamodb", region_name="eu-central-1")

        # Check if any source is selected
        if not any(option for option in options if option.startswith("harvest_")):
            self.print_error("Select at least one harvest-xxx option")
            return

        # Harvest geocat information based on known BOD datasets
        for dataset in BodDataset.objects.iterator():
            if not dataset.fk_geocat:
                self.print_warning(f"Dataset {dataset.id_dataset} has no valid geocat_id")
                continue

            response = get(GEOCAT_URL.format(dataset.fk_geocat), timeout=TIMEOUT)
            if response.status_code != HTTPStatus.OK:
                self.print_warning(f"Dataset {dataset.id_dataset} has no valid geocat entry")
                continue

            try:
                root = etree.fromstring(response.content)
            except etree.LxmlError:
                self.print_warning(f"Dataset {dataset.id_dataset} has no valid geocat XML")
                continue

            if options.get("harvest_keywords"):
                self.harvest_keywords(
                    client, options['target_env'], dataset.id_dataset, dataset.fk_geocat, root
                )

            if options.get("harvest_contacts"):
                self.harvest_contact(
                    client, options['target_env'], dataset.id_dataset, dataset.fk_geocat, root
                )

    def resolve_keyword(self, term: str, keyword: Keyword) -> bool:
        """Resolve the identifier and translations of the given geocat keyword in-place.

        Keywords in geocat refer to concepts defined in thesauri. Unfortunately, geocat only
        returns the concept translations and the thesaurus they belong to. Sometimes, these
        translations are wrong or missing. To resolve this, we try to make a lookup of the concept
        using the specified thesaurus. If a concept has been found, we fill in the concept
        identifier and missing translations.

        Returns True if the keyword was successfully resolved, False otherwise.
        """
        if not term:
            return False

        thesaurus = Thesaurus.get(keyword.thesaurus_url)
        if not thesaurus:
            return False

        concept, translations = thesaurus.find_concept(term)
        if not concept:
            return False

        keyword.concept = concept
        keyword.translation_de = translations.get("de") or keyword.translation_de
        keyword.translation_fr = translations.get("fr") or keyword.translation_fr
        keyword.translation_en = translations.get("en") or keyword.translation_en
        keyword.translation_it = translations.get("it") or keyword.translation_it
        keyword.translation_rm = translations.get("rm") or keyword.translation_rm

        return True

    def harvest_keywords(  # pylint: disable=too-many-positional-arguments,too-many-locals
        self,
        client: "DynamoDBClient",
        env: str,
        dataset_id: str,
        geocat_id: str,
        root: etree._Element
    ) -> None:
        """Get all keywords of a dataset from geocat and store them in the DynamoDB.

        The keywords are ordered by (thesaurus, concept URI).
        """

        self.print(f"Getting keywords for dataset {dataset_id} from geocat")

        keywords = []
        for block in root.findall(".//gmd:MD_Keywords", NS):
            keyword_type = None
            if (element := block.find(".//gmd:MD_KeywordTypeCode", NS)) is not None:
                keyword_type = element.get("codeListValue")

            thesaurus_id = None
            thesaurus_url = None
            if (element := block.find(".//gmd:thesaurusName//gmx:Anchor", NS)) is not None:
                thesaurus_id = element.text
                thesaurus_url = next(
                    (element.get(key) for key in element.keys() if "href" in str(key)),
                    None,
                )

            thesaurus_date = None
            if (element := block.find(".//gmd:thesaurusName//gco:Date", NS)) is not None:
                thesaurus_date = element.text

            for element in block.findall("gmd:keyword", NS):
                if (text := element.find("gco:CharacterString", NS)) is None or not text.text:
                    continue

                translations = {
                    translation.get("locale", "").lstrip("#").lower(): translation.text
                    for translation in element.findall(".//gmd:LocalisedCharacterString", NS)
                    if translation.text
                }

                keyword = Keyword(
                    type=keyword_type,
                    thesaurus_id=thesaurus_id,
                    thesaurus_url=thesaurus_url,
                    thesaurus_date=thesaurus_date,
                    concept=None,
                    translation_de=translations.get("de"),
                    translation_fr=translations.get("fr"),
                    translation_en=translations.get("en"),
                    translation_it=translations.get("it"),
                    translation_rm=translations.get("rm"),
                )
                if not self.resolve_keyword(text.text, keyword):
                    self.print_warning(
                        f"Could not resolve keyword {keyword.concept} in {dataset_id}, skipping"
                    )
                    continue

                keywords.append(keyword)

        keywords.sort(key=lambda k: (k.thesaurus_id or "", k.concept or ""))

        self.print(f"Exporting keywords for dataset {dataset_id} to DynamoDB")
        keyword_list = KeywordList(dataset_id=dataset_id, geocat_id=geocat_id, keywords=keywords)
        client.put_item(TableName=f"harvest-keywords-{env}", Item=keyword_list.as_dynamodb_item())

    def harvest_contact(  # pylint: disable=too-many-positional-arguments
        self,
        client: "DynamoDBClient",
        env: str,
        dataset_id: str,
        geocat_id: str,
        root: etree._Element
    ) -> None:
        """Get all contact information of a dataset from geocat and store them in the DynamoDB."""

        def find(element: etree._Element, path: str) -> str | None:
            return getattr(element.find(path, NS), "text", None)

        contacts: list[Contact] = []
        for block in root.findall(".//gmd:pointOfContact", NS):

            name = find(block, './/gmd:organisationName/gco:CharacterString')
            if not name:
                continue

            role = None
            if (element := block.find(".//gmd:CI_RoleCode", NS)) is not None:
                role = element.attrib.get("codeListValue")

            online_resources = [
                OnlineResource(
                    url=find(resource, ".//gmd:linkage/gmd:URL"),
                    url_de=find(resource, './/che:LocalisedURL[@locale="#DE"]'),
                    url_fr=find(resource, './/che:LocalisedURL[@locale="#FR"]'),
                    url_en=find(resource, './/che:LocalisedURL[@locale="#EN"]'),
                    url_it=find(resource, './/che:LocalisedURL[@locale="#IT"]'),
                    url_rm=find(resource, './/che:LocalisedURL[@locale="#RM"]'),
                    protocol=find(resource, ".//gmd:protocol/*"),
                    name_de=find(resource, './/gmd:name//*[@locale="#DE"]'),
                    name_fr=find(resource, './/gmd:name//*[@locale="#FR"]'),
                    name_en=find(resource, './/gmd:name//*[@locale="#EN"]'),
                    name_it=find(resource, './/gmd:name//*[@locale="#IT"]'),
                    name_rm=find(resource, './/gmd:name//*[@locale="#RM"]'),
                    description_de=find(resource, './/gmd:description//*[@locale="#DE"]'),
                    description_fr=find(resource, './/gmd:description//*[@locale="#FR"]'),
                    description_en=find(resource, './/gmd:description//*[@locale="#EN"]'),
                    description_it=find(resource, './/gmd:description//*[@locale="#IT"]'),
                    description_rm=find(resource, './/gmd:description//*[@locale="#RM"]'),
                ) for resource in block.findall(".//gmd:CI_OnlineResource", NS)
            ]

            online_resources.sort(key=lambda r: r.url or "")

            contact = Contact(
                role=role,
                org_name=name,
                org_name_de=find(block, './/gmd:organisationName//*[@locale="#DE"]'),
                org_name_fr=find(block, './/gmd:organisationName//*[@locale="#FR"]'),
                org_name_en=find(block, './/gmd:organisationName//*[@locale="#EN"]'),
                org_name_it=find(block, './/gmd:organisationName//*[@locale="#IT"]'),
                org_name_rm=find(block, './/gmd:organisationName//*[@locale="#RM"]'),
                org_acronym=find(block, './/che:organisationAcronym/gco:CharacterString'),
                org_acronym_de=find(block, './/che:organisationAcronym//*[@locale="#DE"]'),
                org_acronym_fr=find(block, './/che:organisationAcronym//*[@locale="#FR"]'),
                org_acronym_en=find(block, './/che:organisationAcronym//*[@locale="#EN"]'),
                org_acronym_it=find(block, './/che:organisationAcronym//*[@locale="#IT"]'),
                org_acronym_rm=find(block, './/che:organisationAcronym//*[@locale="#RM"]'),
                org_email=find(block, ".//che:organisationEMail/gco:CharacterString"),
                position_name_de=find(block, './/gmd:positionName//*[@locale="#DE"]'),
                position_name_fr=find(block, './/gmd:positionName//*[@locale="#FR"]'),
                position_name_en=find(block, './/gmd:positionName//*[@locale="#EN"]'),
                position_name_it=find(block, './/gmd:positionName//*[@locale="#IT"]'),
                position_name_rm=find(block, './/gmd:positionName//*[@locale="#RM"]'),
                individual_name=find(block, ".//gmd:individualName/*"),
                individual_first_name=find(block, ".//che:individualFirstName/*"),
                individual_last_name=find(block, ".//che:individualLastName/*"),
                contact_direct_number=find(block, ".//che:directNumber/*"),
                contact_voice=find(block, ".//gmd:voice/*"),
                contact_facsimile=find(block, ".//gmd:facsimile/*"),
                contact_city=find(block, ".//gmd:city/*"),
                contact_administrative_area=find(block, ".//gmd:administrativeArea/*"),
                contact_postal_code=find(block, ".//gmd:postalCode/*"),
                contact_country=find(block, ".//gmd:country/*"),
                contact_electronic_mail_address=find(block, ".//gmd:electronicMailAddress/*"),
                contact_street_name=find(block, ".//che:streetName/*"),
                contact_street_number=find(block, ".//che:streetNumber/*"),
                contact_post_box=find(block, ".//che:postBox/*"),
                hours_of_service=find(block, ".//gmd:hoursOfService/*"),
                contact_instructions=find(block, ".//gmd:contactInstructions/*"),
                online_resources=online_resources
            )

            contacts.append(contact)

        contacts.sort(key=lambda c: (c.role or "", c.org_name_de or "", c.org_name_fr or ""))

        self.print(f"Exporting contacts for dataset {dataset_id} to DynamoDB")
        contact_list = ContactList(dataset_id=dataset_id, geocat_id=geocat_id, contacts=contacts)
        client.put_item(TableName=f"harvest-contacts-{env}", Item=contact_list.as_dynamodb_item())
