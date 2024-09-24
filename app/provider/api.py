from ninja import Router
from utils.translation import LanguageCode
from utils.translation import get_translation

from django.shortcuts import get_object_or_404

from .models import Provider
from .schemas import ProviderSchema
from .schemas import TranslationsSchema

router = Router()


@router.get("/providers/{provider_id}", response={200: ProviderSchema})
def provider(request, provider_id: str, lang: LanguageCode = LanguageCode.ENGLISH):

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
