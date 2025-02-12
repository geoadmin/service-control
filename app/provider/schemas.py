from ninja import Schema
from schemas import TranslationsSchema


class ProviderSchema(Schema):
    id: str
    name: str
    name_translations: TranslationsSchema
    acronym: str
    acronym_translations: TranslationsSchema


class ProviderListSchema(Schema):
    items: list[ProviderSchema]
