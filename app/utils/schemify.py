from provider.models import Provider
from provider.schemas import ProviderSchema
from provider.schemas import TranslationsSchema
from utils.language import LanguageCode
from utils.language import get_translation


class ProviderModelMapper:

    @staticmethod
    def to_schema(model: Provider, lang: LanguageCode) -> ProviderSchema:
        schema = ProviderSchema(
            id=str(model.id),
            name=get_translation(model, "name", lang),
            name_translations=TranslationsSchema(
                de=model.name_de,
                fr=model.name_fr,
                en=model.name_en,
                it=model.name_it,
                rm=model.name_rm,
            ),
            acronym=get_translation(model, "acronym", lang),
            acronym_translations=TranslationsSchema(
                de=model.acronym_de,
                fr=model.acronym_fr,
                en=model.acronym_en,
                it=model.acronym_it,
                rm=model.acronym_rm,
            )
        )
        return schema
