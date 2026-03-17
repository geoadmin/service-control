from typing import Any

from pydantic import BaseModel


class BaseModelWithDynamoDBSerialization(BaseModel):
    """BaseModel with custom serialization for DynamoDB"""

    def as_dynamodb_item(self) -> dict[str, Any]:
        """Convert the dataset to a DynamoDB item format

        Returns:
            dict[str, Any]: The dataset represented as a DynamoDB item.
        """

        def serialize(value: Any) -> dict[str, Any]:
            if value is None:
                return {"NULL": True}
            if isinstance(value, int):
                return {"N": str(value)}
            if isinstance(value, str):
                return {"S": value}
            if isinstance(value, list):
                return {"L": [serialize(i) for i in value]}
            if isinstance(value, dict):
                return {"M": {k: serialize(v) for k, v in value.items()}}
            raise ValueError(f"Unexpected type {type(value)}")

        item = self.model_dump(mode="json")
        return {key: serialize(value) for key, value in item.items()}


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
    thesaurus: str | None
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
