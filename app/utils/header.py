from typing import Final

from .language import LanguageCode

# to prevent possible denial of service or memory exhaustion attacks
ACCEPT_LANGUAGE_HEADER_MAX_LENGTH: Final = 500
DEFAULT_LANGUAGE: Final = LanguageCode.ENGLISH


def extract_lang(accept_lang_header: str) -> LanguageCode:
    """
    Extract the first supported language from the HTTP header "Accept-Language".

    Examples:

        "fr;q=0.5, de-CH;q=0.7" --> "fr"
        "ru, de-CH,*"           --> "de"
        "zh-CN, es-ES, li"      --> "en"
    """
    if len(accept_lang_header) > ACCEPT_LANGUAGE_HEADER_MAX_LENGTH:
        return DEFAULT_LANGUAGE

    for lang_with_q in accept_lang_header.split(","):
        stripped = lang_with_q.strip()
        lang_with_subtag = stripped.split(";", maxsplit=1)[0]
        lang = lang_with_subtag.split("-", maxsplit=1)[0]
        if lang in LanguageCode:
            return LanguageCode(lang)

    return DEFAULT_LANGUAGE
