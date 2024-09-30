from enum import StrEnum
from typing import Any
from typing import Final

from django.http.request import HttpHeaders

from .header import extract_lang


class LanguageCode(StrEnum):
    """
    Two-letter language codes
    """
    GERMAN = "de"
    FRENCH = "fr"
    ITALIAN = "it"
    ROMANSH = "rm"
    ENGLISH = "en"


DEFAULT_LANGUAGE: Final = LanguageCode.ENGLISH


def get_language(lang_query_param: str | None, headers: HttpHeaders) -> LanguageCode:
    """
    Take the language from the given query parameter or resort to the header if not available.

    If no valid language was found in either of the two, resort to the default language.
    """
    if lang_query_param and lang_query_param in LanguageCode:
        return LanguageCode(lang_query_param)

    if "Accept-Language" not in headers:
        return DEFAULT_LANGUAGE

    lang_header = headers["Accept-Language"]
    lang = extract_lang(lang_header, list(LanguageCode))
    if not lang:
        return DEFAULT_LANGUAGE
    return LanguageCode(lang)


def get_translation(
    obj: Any,
    field_name: str,
    lang: LanguageCode,
    default_lang: LanguageCode = LanguageCode.ENGLISH
) -> str:
    """
    Return the field `obj.{field_name}_{lang}` as a string if it has a value.

    This facilitates getting a field of a defined language in a class that has
    many fields like

         name_de
         name_fr
         name_it
         name_en
         name_rm

    If the field is not present in the given object or if it's value is empty
    or None, the field with the given default language is returned.
    If that default is not available either, an AttributeError exception is raised.
    """
    try:
        translation = getattr(obj, f"{field_name}_{lang}")
        if not translation:
            raise AttributeError
        return str(translation)
    except AttributeError as exception:
        default_name = f"{field_name}_{default_lang}"
        default = getattr(obj, default_name)
        if not default:
            raise exception
        return str(default)
