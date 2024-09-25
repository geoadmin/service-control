from utils.header import extract_lang


def test_extract_lang_returns_language_if_only_one_valid():
    assert extract_lang("de") == "de"


def test_extract_lang_ignores_subtag_for_single_language():
    assert extract_lang("de-CH") == "de"


def test_extract_lang_ignores_subtag_for_multiple_languages():
    assert extract_lang("zh-CN, it-IT") == "it"


def test_extract_lang_ignores_wildcard_for_single_language():
    assert extract_lang("*") == "en"


def test_extract_lang_ignores_wildcard_for_multiple_languages():
    assert extract_lang("*, rm") == "rm"


def test_extract_lang_returns_first_valid_language():
    assert extract_lang("zh-CN, fr, en") == "fr"


def test_extract_lang_returns_default_if_none_valid():
    assert extract_lang("*, bla, ru") == "en"


def test_extract_lang_returns_default_if_empty():
    assert extract_lang("") == "en"


def test_extract_lang_returns_valid_language_with_largest_q_factor():
    assert extract_lang("ru;q=0.9, de;q=0.7, rm;q=0.8") == "rm"
