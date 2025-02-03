from datetime import datetime

from ninja import Schema
from schemas import TranslationsSchema


class AttributionSchema(Schema):
    id: int
    slug: str
    name: str
    name_translations: TranslationsSchema
    description: str
    description_translations: TranslationsSchema
    provider_id: int


class AttributionListSchema(Schema):
    items: list[AttributionSchema]


class DatasetSchema(Schema):
    id: int
    slug: str
    created: datetime
    updated: datetime
    provider_id: int
    attribution_id: int


class DatasetListSchema(Schema):
    items: list[DatasetSchema]
