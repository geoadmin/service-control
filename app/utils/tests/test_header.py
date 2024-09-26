from utils.header import extract_lang


def test_extract_lang_returns_language_if_only_one_valid():
    assert extract_lang("de", ["de"]) == "de"


def test_extract_lang_ignores_subtag_for_single_language():
    assert extract_lang("de-CH", ["de"]) == "de"


def test_extract_lang_ignores_subtag_for_multiple_languages():
    assert extract_lang("zh-CN, it-IT", ["it"]) == "it"


def test_extract_lang_ignores_wildcard_for_single_language():
    assert extract_lang("*", ["de"]) is None


def test_extract_lang_ignores_wildcard_for_multiple_languages():
    assert extract_lang("*, rm", ["rm"]) == "rm"


def test_extract_lang_returns_first_valid_language():
    assert extract_lang("zh-CN, fr, en", ["fr", "en"]) == "fr"


def test_extract_lang_returns_none_if_no_valid_language():
    assert extract_lang("*, bla, ru", ["de", "fr", "it"]) is None


def test_extract_lang_returns_none_if_empty():
    assert extract_lang("", ["en"]) is None


def test_extract_lang_returns_first_valid_language_ignoring_q_factor():
    assert extract_lang("ru;q=0.9, de;q=0.7, rm;q=0.8", ["de", "fr"]) == "de"
