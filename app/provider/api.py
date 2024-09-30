from ninja import Router
from utils.language import LanguageCode
from utils.language import get_language
from utils.schemify import ProviderModelMapper

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import Provider
from .schemas import ProviderListSchema
from .schemas import ProviderSchema

router = Router()


@router.get("/{provider_id}", response={200: ProviderSchema}, exclude_none=True)
def provider(request: HttpRequest, provider_id: int, lang: LanguageCode | None = None):
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

        - For multiple languages, the first valid language is taken, so q-factors
          are ignored (Example: "de;q=0.7, rm;q=0.8" --> "de")
        - Subtags in the header are ignored. So "en-US" is interpreted as "en".
        - Wildcards ("*") are ignored.
    """
    lang_to_use = get_language(lang, request.headers)

    model = get_object_or_404(Provider, id=provider_id)
    schema = ProviderModelMapper.to_schema(model, lang_to_use)
    return schema


@router.get("/", response={200: ProviderListSchema}, exclude_none=True)
def providers(request: HttpRequest, lang: LanguageCode | None = None):
    """
    Get all providers, return translatable fields in the given language.

    For more details on how individual providers are returned, see the
    corresponding endpoint for a specific provider.
    """
    lang_to_use = get_language(lang, request.headers)

    models = Provider.objects.order_by("id").all()
    schemas = [ProviderModelMapper.to_schema(model, lang_to_use) for model in models]
    return ProviderListSchema(items=schemas)
