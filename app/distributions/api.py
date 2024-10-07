from ninja import Router
from schemas import TranslationsSchema
from utils.language import LanguageCode
from utils.language import get_language
from utils.language import get_translation

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import Attribution
from .models import Dataset
from .schemas import AttributionListSchema
from .schemas import AttributionSchema
from .schemas import DatasetListSchema
from .schemas import DatasetSchema

router = Router()


def attribution_to_response(model: Attribution, lang: LanguageCode) -> AttributionSchema:
    """
    Transforms the given model using the given language into a response object.
    """
    response = AttributionSchema(
        id=str(model.id),
        name=get_translation(model, "name", lang),
        name_translations=TranslationsSchema(
            de=model.name_de,
            fr=model.name_fr,
            en=model.name_en,
            it=model.name_it,
            rm=model.name_rm,
        ),
        description=get_translation(model, "description", lang),
        description_translations=TranslationsSchema(
            de=model.description_de,
            fr=model.description_fr,
            en=model.description_en,
            it=model.description_it,
            rm=model.description_rm,
        ),
        provider_id=str(model.provider.id),
    )
    return response


@router.get("attributions/{attribution_id}", response={200: AttributionSchema}, exclude_none=True)
def attribution(request: HttpRequest, attribution_id: int, lang: LanguageCode | None = None):
    """
    Get the attribution with the given ID, return translatable fields in the given language.

    Example: If German ("de") is set as the language of choice, fields "name" and
             "description" would take the value of the corresponding translation.

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
                    "description": "DE",
                    "description_translations": {
                        "de": "DE",
                        "fr": "FR",
                        "en": "EN",
                        "it": "IT",
                        "rm": "RM",
                    },
                    provider_id: 123
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
    model = get_object_or_404(Attribution, id=attribution_id)
    lang_to_use = get_language(lang, request.headers)
    response = attribution_to_response(model, lang_to_use)
    return response


@router.get("attributions", response={200: AttributionListSchema}, exclude_none=True)
def attributions(request: HttpRequest, lang: LanguageCode | None = None):
    """
    Get all attributions, return translatable fields in the given language.

    For more details on how individual attributions are returned, see the
    corresponding endpoint for a specific attribution.
    """
    models = Attribution.objects.order_by("id").all()
    lang_to_use = get_language(lang, request.headers)

    responses = [attribution_to_response(model, lang_to_use) for model in models]
    return AttributionListSchema(items=responses)


def dataset_to_response(model: Dataset) -> DatasetSchema:
    """
    Transforms the given model into a response object.
    """
    return DatasetSchema(
        id=str(model.id),
        slug=model.slug,
        created=model.created,
        updated=model.updated,
        provider_id=str(model.provider.id),
        attribution_id=str(model.attribution.id),
    )


@router.get("datasets/{dataset_id}", response={200: DatasetSchema}, exclude_none=True)
def dataset(request: HttpRequest, dataset_id: int):
    """
    Get the dataset with the given ID.
    """
    model = get_object_or_404(Dataset, id=dataset_id)
    response = dataset_to_response(model)
    return response


@router.get("datasets", response={200: DatasetListSchema}, exclude_none=True)
def datasets(request: HttpRequest):
    """
    Get all datasets.

    For more details on how individual datasets are returned, see the
    corresponding endpoint for a specific attribution.
    """
    models = Dataset.objects.order_by("id").all()
    responses = [dataset_to_response(model) for model in models]
    return DatasetListSchema(items=responses)