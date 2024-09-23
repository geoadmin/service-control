from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Provider
from .schemas import ProviderSchema, TranslationsSchema

router = Router()


@router.get("/providers/{provider_id}", response={200: ProviderSchema})
def provider(request, provider_id: str):
    provider_object = get_object_or_404(Provider, id=provider_id)
    schema = ProviderSchema(
        id=str(provider_object.id),
        name_translations=TranslationsSchema(
            de=provider_object.name_de,
            fr=provider_object.name_fr,
            en=provider_object.name_en,
            it=provider_object.name_it,
            rm=provider_object.name_rm,
        ),
        acronym_translations=TranslationsSchema(
            de=provider_object.acronym_de,
            fr=provider_object.acronym_fr,
            en=provider_object.acronym_en,
            it=provider_object.acronym_it,
            rm=provider_object.acronym_rm,
        )
    )
    return schema
