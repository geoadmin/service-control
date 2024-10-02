from ninja import Schema
from schemas import TranslationsSchema


class AttributionSchema(Schema):
    id: str
    name: str
    name_translations: TranslationsSchema
    description: str
    description_translations: TranslationsSchema
    provider_id: str
