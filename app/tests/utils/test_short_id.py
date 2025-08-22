from utils.short_id import generate_short_id


def test_generate_short_id_default():
    short_id_1 = generate_short_id()
    short_id_2 = generate_short_id()
    assert short_id_1 != short_id_2
    assert len(short_id_1) == 12
    assert len(short_id_2) == 12


def test_generate_short_id_settings(settings):
    settings.SHORT_ID_SIZE = 4
    settings.SHORT_ID_ALPHABET = "a"
    short_id = generate_short_id()
    assert short_id == "aaaa"
