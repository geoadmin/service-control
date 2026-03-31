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
    org_email: str | None
    position_name_de: str | None
    position_name_fr: str | None
    position_name_en: str | None
    position_name_it: str | None
    position_name_rm: str | None
    individual_name: str | None
    individual_first_name: str | None
    individual_last_name: str | None
    contact_direct_number: str | None
    contact_voice: str | None
    contact_facsimile: str | None
    contact_city: str | None
    contact_administrative_area: str | None
    contact_postal_code: str | None
    contact_country: str | None
    contact_electronic_mail_address: str | None
    contact_street_name: str | None
    contact_street_number: str | None
    contact_post_box: str | None
    hours_of_service: str | None
    contact_instructions: str | None
    online_resources: list[OnlineResource]


class ContactList(BaseModelWithDynamoDBSerialization):
    dataset_id: str
    geocat_id: str
    contacts: list[Contact]
