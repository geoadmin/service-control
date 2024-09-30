from typing import Final

# to prevent possible denial of service or memory exhaustion attacks
ACCEPT_LANGUAGE_HEADER_MAX_LENGTH: Final = 500


def extract_lang(accept_lang_header: str, valid_langs: list[str]) -> str | None:
    """
    Extract the first valid language from the HTTP header "Accept-Language".

    Return None if there is no valid language or if the header is too long.
    """
    if len(accept_lang_header) > ACCEPT_LANGUAGE_HEADER_MAX_LENGTH:
        return None

    for lang_with_q in accept_lang_header.split(","):
        stripped = lang_with_q.strip()
        lang_with_subtag = stripped.split(";", maxsplit=1)[0]
        lang = lang_with_subtag.split("-", maxsplit=1)[0]
        if lang in valid_langs:
            return lang

    return None
