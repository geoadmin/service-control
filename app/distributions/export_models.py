from decimal import Decimal
from typing import Any

from boto3.dynamodb.types import TypeSerializer
from pydantic import BaseModel


class BaseModelWithDynamoDBSerialization(BaseModel):
    """BaseModel with custom serialization for DynamoDB"""

    def as_dynamodb_item(self) -> dict[str, Any]:
        """Convert the dataset to a DynamoDB item format

        Returns:
            dict[str, Any]: The dataset represented as a DynamoDB item.
        """
        serializer = TypeSerializer()
        item = self.model_dump()
        return {key: serializer.serialize(value) for key, value in item.items()}


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


class Keyword(BaseModel):
    type: str | None
    thesaurus_id: str | None
    thesaurus_url: str | None
    thesaurus_date: str | None
    concept: str | None
    translation_de: str | None
    translation_fr: str | None
    translation_en: str | None
    translation_it: str | None
    translation_rm: str | None


class KeywordList(BaseModelWithDynamoDBSerialization):
    dataset_id: str
    geocat_id: str
    keywords: list[Keyword]


class OnlineResource(BaseModel):
    url: str | None
    url_de: str | None
    url_fr: str | None
    url_en: str | None
    url_it: str | None
    url_rm: str | None
    protocol: str | None
    name_de: str | None
    name_fr: str | None
    name_en: str | None
    name_it: str | None
    name_rm: str | None
    description_de: str | None
    description_fr: str | None
    description_en: str | None
    description_it: str | None
    description_rm: str | None
    function: str | None


class Contact(BaseModel):
    role: str | None
    org_name: str | None
    org_name_de: str | None
    org_name_fr: str | None
    org_name_en: str | None
    org_name_it: str | None
    org_name_rm: str | None
    org_acronym: str | None
    org_acronym_de: str | None
    org_acronym_fr: str | None
    org_acronym_en: str | None
    org_acronym_it: str | None
    org_acronym_rm: str | None
    position_name_de: str | None
    position_name_fr: str | None
    position_name_en: str | None
    position_name_it: str | None
    position_name_rm: str | None
    contact_voice: str | None
    contact_facsimile: str | None
    contact_sms: str | None
    contact_city: str | None
    contact_administrative_area: str | None
    contact_postal_code: str | None
    contact_country: str | None
    contact_electronic_mail_addresses: list[str]
    contact_delivery_point: str | None
    online_resources: list[OnlineResource]


class ContactList(BaseModelWithDynamoDBSerialization):
    dataset_id: str
    geocat_id: str
    contacts: list[Contact]


class ExportLayersJS(BaseModelWithDynamoDBSerialization):
    layer_id: str
    bod_layer_id: str | None = None
    topics: str | None = None
    chargeable: bool | None = None
    staging: str | None = None
    server_layername: str | None = None
    attribution: str | None = None
    layertype: str | None = None
    opacity: Decimal | None = None
    minresolution: Decimal | None = None
    maxresolution: Decimal | None = None
    extent: list[Decimal] | None = None
    backgroundlayer: bool | None = None
    tooltip: bool | None = None
    searchable: bool | None = None
    timeenabled: bool | None = None
    haslegend: bool | None = None
    singletile: bool | None = None
    highlightable: bool | None = None
    wms_layers: str | None = None
    time_behaviour: str | None = None
    image_format: str | None = None
    tilematrix_resolution_max: Decimal | None = None
    timestamps: list[str | None] | None = None
    parentlayerid: str | None = None
    sublayersids: list[str | None] | None = None
    time_get_parameter: str | None = None
    time_format: str | None = None
    wms_gutter: int | None = None
    sphinx_index: str | None = None
    geojson_url_de: str | None = None
    geojson_url_fr: str | None = None
    geojson_url_it: str | None = None
    geojson_url_en: str | None = None
    geojson_url_rm: str | None = None
    geojson_update_delay: int | None = None
    srid: str | None = None
