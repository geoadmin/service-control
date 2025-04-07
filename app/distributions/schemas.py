from datetime import datetime

from ninja import Schema
from schemas import TranslationsSchema


class AttributionSchema(Schema):
    id: str
    name: str
    name_translations: TranslationsSchema
    description: str
    description_translations: TranslationsSchema
    provider_id: str


class AttributionListSchema(Schema):
    items: list[AttributionSchema]


class DatasetSchema(Schema):
    id: str
    title: str
    title_translations: TranslationsSchema
    description: str
    description_translations: TranslationsSchema
    created: datetime
    updated: datetime
    provider_id: str
    attribution_id: str


class DatasetListSchema(Schema):
    items: list[DatasetSchema]
