from ninja import Schema


class TranslationsSchema(Schema):
    de: str
    fr: str
    en: str
    it: str | None
    rm: str | None


class ProviderSchema(Schema):
    id: str
    name: str
    name_translations: TranslationsSchema
    acronym: str
    acronym_translations: TranslationsSchema


class ProviderListSchema(Schema):
    items: list[ProviderSchema]
