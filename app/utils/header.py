from acceptlang import parse_accept_lang_header

from .translation import LanguageCode


def extract_lang(accept_lang_header: str) -> LanguageCode:
    """
    Extract the supported language from the HTTP header "Accept-Language".

    Examples:

        "fr;q=0.5, de-CH;q=0.7" --> "de"
        "ru, de-CH,*"           --> "de"
        "zh-CN, es-ES, li"      --> "en"

    To consider:

        - The supported languages are: "de", "fr", "it", "en", "rm".
        - For multiple languages, the valid language with the largest q-factor
          (";q=0.8") is taken. If no valid language was found, "en" is returned.
        - Subtags are ignored, so "en-US" becomes "en".
        - Wildcards ("*") are ignored
    """
    parsed = parse_accept_lang_header(accept_lang_header)

    for lang_with_subtag, _ in parsed:
        lang = lang_with_subtag.split("-")[0]
        # as acceptlang orders by decreasing q-factor, we can stop at the first
        if lang in LanguageCode:
            return LanguageCode(lang)

    return LanguageCode.ENGLISH
