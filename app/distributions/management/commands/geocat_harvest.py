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
    "cat": "http://standards.iso.org/iso/19115/-3/cat/1.0",
    "che": "http://geocat.ch/che",
    "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    "dqm": "http://standards.iso.org/iso/19157/-2/dqm/1.0",
    "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    "gcx": "http://standards.iso.org/iso/19115/-3/gcx/1.0",
    "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
    "gfc": "http://standards.iso.org/iso/19110/gfc/1.1",
    "gml": "http://www.opengis.net/gml/3.2",
    "lan": "http://standards.iso.org/iso/19115/-3/lan/1.0",
    "mac": "http://standards.iso.org/iso/19115/-3/mac/2.0",
    "mas": "http://standards.iso.org/iso/19115/-3/mas/1.0",
    "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
    "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
    "md1": "http://standards.iso.org/iso/19115/-3/md1/2.0",
    "md2": "http://standards.iso.org/iso/19115/-3/md2/2.0",
    "mda": "http://standards.iso.org/iso/19115/-3/mda/2.0",
    "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0",
    "mdq": "http://standards.iso.org/iso/19157/-2/mdq/1.0",
    "mds": "http://standards.iso.org/iso/19115/-3/mds/2.0",
    "mdt": "http://standards.iso.org/iso/19115/-3/mdt/2.0",
    "mex": "http://standards.iso.org/iso/19115/-3/mex/1.0",
    "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
    "mpc": "http://standards.iso.org/iso/19115/-3/mpc/1.0",
    "mrc": "http://standards.iso.org/iso/19115/-3/mrc/2.0",
    "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
    "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
    "mrl": "http://standards.iso.org/iso/19115/-3/mrl/2.0",
    "mrs": "http://standards.iso.org/iso/19115/-3/mrs/1.0",
    "msr": "http://standards.iso.org/iso/19115/-3/msr/2.0",
    "srv": "http://standards.iso.org/iso/19115/-3/srv/2.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
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
        for block in root.findall(".//mri:MD_Keywords", NS):
            keyword_type = None
            if (element := block.find(".//mri:MD_KeywordTypeCode", NS)) is not None:
                keyword_type = element.get("codeListValue")

            # Note: eCH defines the thesaurus id as mcc:code only very vaguely as "Zeichenfolge".
            #       In reality this is typically encapsulated in an gcx:Anchor. But other examples
            #       (outside of thesauri) of mcc:code encapsulate this in a gco:CharacterString.
            thesaurus_id = None
            thesaurus_url = None
            if (
                element :=
                block.find(".//mri:thesaurusName//cit:identifier//mcc:code//gcx:Anchor", NS)
            ) is not None:
                thesaurus_id = element.text
                thesaurus_url = next(
                    (element.get(key) for key in element.keys() if "href" in str(key)),
                    None,
                )
            elif (
                element := block.find(
                    ".//mri:thesaurusName//cit:identifier//mcc:code//gco:CharacterString", NS
                )
            ) is not None:
                thesaurus_id = element.text
            elif (
                element := block.find(".//mri:thesaurusName//cit:identifier//mcc:code", NS)
            ) is not None:
                thesaurus_id = element.text

            if thesaurus_id:
                thesaurus_id = thesaurus_id.strip()

            # Note: eCH defines different types of dates (publication, update etc.), we only care
            #       about the last of these
            thesaurus_dates = sorted({
                str(element.text)
                for element in block.findall(".//mri:thesaurusName//gco:Date", NS)
            })
            thesaurus_date = thesaurus_dates[-1] if thesaurus_dates else None

            for element in block.findall("mri:keyword", NS):
                if (text := element.find("gco:CharacterString", NS)) is None or not text.text:
                    continue

                translations = {
                    translation.get("locale", "").lstrip("#").lower(): translation.text
                    for translation in element.findall(".//lan:LocalisedCharacterString", NS)
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

    def harvest_contact(  # pylint: disable=too-many-positional-arguments,too-many-locals
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

        def find_code(element: etree._Element, path: str) -> str | None:
            if (result := element.find(path, NS)) is not None:
                return result.attrib.get("codeListValue")
            return None

        contacts: list[Contact] = []
        for block in root.findall(".//mri:pointOfContact", NS):

            name = find(block, './/che:CHE_CI_Organisation/cit:name/gco:CharacterString')
            if not name:
                continue

            role = find_code(block, ".//cit:CI_RoleCode")

            online_resources = [
                OnlineResource(
                    url=find(resource, ".//cit:linkage/gco:CharacterString"),
                    url_de=find(resource, './/cit:linkage//*[@locale="#DE"]'),
                    url_fr=find(resource, './/cit:linkage//*[@locale="#FR"]'),
                    url_en=find(resource, './/cit:linkage//*[@locale="#EN"]'),
                    url_it=find(resource, './/cit:linkage//*[@locale="#IT"]'),
                    url_rm=find(resource, './/cit:linkage//*[@locale="#RM"]'),
                    protocol=find(resource, ".//cit:protocol/*"),
                    name_de=find(resource, './/cit:name//*[@locale="#DE"]'),
                    name_fr=find(resource, './/cit:name//*[@locale="#FR"]'),
                    name_en=find(resource, './/cit:name//*[@locale="#EN"]'),
                    name_it=find(resource, './/cit:name//*[@locale="#IT"]'),
                    name_rm=find(resource, './/cit:name//*[@locale="#RM"]'),
                    description_de=find(resource, './/cit:description//*[@locale="#DE"]'),
                    description_fr=find(resource, './/cit:description//*[@locale="#FR"]'),
                    description_en=find(resource, './/cit:description//*[@locale="#EN"]'),
                    description_it=find(resource, './/cit:description//*[@locale="#IT"]'),
                    description_rm=find(resource, './/cit:description//*[@locale="#RM"]'),
                    function=find_code(resource, ".//cit:function/*"),
                ) for resource in block.findall(".//cit:CI_OnlineResource", NS)
            ]
            online_resources.sort(key=lambda r: r.url or "")

            phone_numbers = {
                find(resource, ".//cit:CI_TelephoneTypeCode"):
                    find(resource, ".//cit:number/gco:CharacterString")
                for resource in block.findall(".//cit:CI_Telephone", NS)
            }

            emails = [
                email for element in block.findall(".//cit:electronicMailAddress//*", NS)
                if (email := getattr(element, "text", None))
            ]

            contact = Contact(
                role=role,
                org_name=name,
                org_name_de=find(block, './/che:CHE_CI_Organisation/cit:name//*[@locale="#DE"]'),
                org_name_fr=find(block, './/che:CHE_CI_Organisation/cit:name//*[@locale="#FR"]'),
                org_name_en=find(block, './/che:CHE_CI_Organisation/cit:name//*[@locale="#EN"]'),
                org_name_it=find(block, './/che:CHE_CI_Organisation/cit:name//*[@locale="#IT"]'),
                org_name_rm=find(block, './/che:CHE_CI_Organisation/cit:name//*[@locale="#RM"]'),
                org_acronym=find(block, './/che:organisationAcronym/gco:CharacterString'),
                org_acronym_de=find(block, './/che:organisationAcronym//*[@locale="#DE"]'),
                org_acronym_fr=find(block, './/che:organisationAcronym//*[@locale="#FR"]'),
                org_acronym_en=find(block, './/che:organisationAcronym//*[@locale="#EN"]'),
                org_acronym_it=find(block, './/che:organisationAcronym//*[@locale="#IT"]'),
                org_acronym_rm=find(block, './/che:organisationAcronym//*[@locale="#RM"]'),
                position_name_de=find(block, './/cit:CI_Individual//*[@locale="#DE"]'),
                position_name_fr=find(block, './/cit:CI_Individual//*[@locale="#FR"]'),
                position_name_en=find(block, './/cit:CI_Individual//*[@locale="#EN"]'),
                position_name_it=find(block, './/cit:CI_Individual//*[@locale="#IT"]'),
                position_name_rm=find(block, './/cit:CI_Individual//*[@locale="#RM"]'),
                contact_voice=phone_numbers.get('voice'),
                contact_facsimile=phone_numbers.get('facsimile'),
                contact_sms=phone_numbers.get('sms'),
                contact_city=find(block, ".//cit:city/*"),
                contact_administrative_area=find(block, ".//cit:administrativeArea/*"),
                contact_postal_code=find(block, ".//cit:postalCode/*"),
                contact_country=find(block, ".//cit:country/*"),
                contact_electronic_mail_addresses=emails,
                contact_delivery_point=find(block, ".//cit:deliveryPoint/*"),
                online_resources=online_resources
            )

            contacts.append(contact)

        contacts.sort(key=lambda c: (c.role or "", c.org_name_de or "", c.org_name_fr or ""))

        self.print(f"Exporting contacts for dataset {dataset_id} to DynamoDB")
        contact_list = ContactList(dataset_id=dataset_id, geocat_id=geocat_id, contacts=contacts)
        client.put_item(TableName=f"harvest-contacts-{env}", Item=contact_list.as_dynamodb_item())
