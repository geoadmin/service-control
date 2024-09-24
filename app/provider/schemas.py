from ninja import Schema


class TranslationsSchema(Schema):
    de: str
    fr: str
    en: str
    it: str
    rm: str


class ProviderSchema(Schema):
    id: str
    name: str
    name_translations: TranslationsSchema
    acronym: str
    acronym_translations: TranslationsSchema
