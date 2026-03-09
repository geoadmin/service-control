from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class DynamoDBEncoderError(ValueError):
    """Custom error for DynamoDB encoding issues"""


class BaseModelWithDynamoDBSerialization(BaseModel):
    """BaseModel with custom serialization for DynamoDB"""

    def as_dynamodb_item(self) -> dict[str, Any]:
        """Convert the dataset to a DynamoDB item format

        Returns:
            dict[str, Any]: The dataset represented as a DynamoDB item.
        """
        item = self.model_dump(mode="python")
        for key, value in item.items():
            item[key] = self.handle_value(value)
        return item

    def handle_value(self, value: Any) -> dict[str, Any]:
        """Handle the conversion of a value to DynamoDB format

        Args:
            value (Any): The value to convert

        Returns:
            dict[str, Any]: The value converted to DynamoDB format
        """
        if value is None:
            return {"NULL": True}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif (
            isinstance(value, int)
            or isinstance(value, float)
            or isinstance(value, Decimal)
        ):
            return {"N": str(value)}
        elif isinstance(value, str):
            return {"S": value}
        elif isinstance(value, list):
            return {"L": [self.handle_value(i) for i in value]}
        else:
            raise DynamoDBEncoderError(
                f"Unsupported type {type(value)} for value {value}"
            )


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
    timestamps: list[str] | None = None
    parentlayerid: str | None = None
    sublayersids: list[str] | None = None
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
