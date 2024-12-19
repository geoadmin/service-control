from ninja import Schema


class TranslationsSchema(Schema):
    de: str
    fr: str
    en: str
    it: str | None
    rm: str | None
