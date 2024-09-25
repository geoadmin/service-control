from ninja import Router
from utils.header import extract_lang
from utils.translation import LanguageCode
from utils.translation import get_translation

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import Provider
from .schemas import ProviderSchema
from .schemas import TranslationsSchema

router = Router()


@router.get("/providers/{provider_id}", response={200: ProviderSchema}, exclude_none=True)
def provider(request: HttpRequest, provider_id: str, lang: LanguageCode | None = None):
    """
    Get the provider with the given ID, return translatable fields in the given language.

    Example: If German ("de") is set as the language of choice, fields "name" and
             "acronym" would take the value of the corresponding translation.

                {
                    "id": "1",
                    "name": "German",
                    "name_translations": {
                        "de": "German",
                        "fr": "French",
                        "en": "English",
                        "it": "Italian",
                        "rm": "Romansh",
                    },
                    "acronym": "DE",
                    "acronym_translations": {
                        "de": "DE",
                        "fr": "FR",
                        "en": "EN",
                        "it": "IT",
                        "rm": "RM",
                    }
                }

    The language can be set via

        1. Query parameter. For example: "lang=de"
        2. Header "Accept-Language". For example: "Accept-Language: de"

    To consider for the language setting:

        - If both query param and header are set, the query param is taken.
        - The valid languages are: "de", "fr", "en", "it", "rm"
        - If no language is specified, English is taken as the default.

    To consider for the header "Accept-Language":

        - For multiple languages, the valid language with the largest q-factor
          is taken (Example: "de;q=0.7, rm;q=0.8" --> "rm")
        - Subtags in the header are ignored. So "en-US" is interpreted as "en".
        - Wildcards ("*") are ignored.
    """
    if not lang:
        if "Accept-Language" in request.headers:
            lang_header = request.headers["Accept-Language"]
            lang = extract_lang(lang_header)
        else:
            lang = LanguageCode.ENGLISH

    provider_object = get_object_or_404(Provider, id=provider_id)
    schema = ProviderSchema(
        id=str(provider_object.id),
        name=get_translation(provider_object, "name", lang),
        name_translations=TranslationsSchema(
            de=provider_object.name_de,
            fr=provider_object.name_fr,
            en=provider_object.name_en,
            it=provider_object.name_it,
            rm=provider_object.name_rm,
        ),
        acronym=get_translation(provider_object, "acronym", lang),
        acronym_translations=TranslationsSchema(
            de=provider_object.acronym_de,
            fr=provider_object.acronym_fr,
            en=provider_object.acronym_en,
            it=provider_object.acronym_it,
            rm=provider_object.acronym_rm,
        )
    )
    return schema
