import json
from functools import cache
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

from bod.models import BodDataset
from boto3 import Session
from distributions.export_models import Keyword
from distributions.export_models import KeywordList
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
    harvesting tables. Currently supports only dataset keywords.

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

    def handle(self, *args: Any, **options: Any) -> None:
        """Main entry point of command."""

        # Show parsed arguments (useful for debugging)
        if options.get("verbosity", 0) >= 2:
            self.print(f"Debug: parsed args = {json.dumps(options)}")

        # Create DynamoDB client
        session = Session(profile_name=options["profile_name"])
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

        thesaurus = Thesaurus.get(keyword.thesaurus)
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

    def harvest_keywords(  # pylint: disable=too-many-positional-arguments
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

            thesaurus = None
            if (element := block.find(".//gmd:thesaurusName//gmx:Anchor", NS)) is not None:
                thesaurus = next(
                    (element.get(key) for key in element.keys() if "href" in str(key)),
                    None,
                )

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
                    thesaurus=thesaurus,
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

        keywords = sorted(keywords, key=lambda k: (str(k.thesaurus), str(k.concept)))

        self.print(f"Exporting keywords for dataset {dataset_id} to DynamoDB")
        keyword_list = KeywordList(dataset_id=dataset_id, geocat_id=geocat_id, keywords=keywords)
        client.put_item(TableName=f"harvest-keywords-{env}", Item=keyword_list.as_dynamodb_item())
