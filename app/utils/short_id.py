from nanoid import generate

from django.conf import settings


def generate_short_id() -> str:
    """ Generate a Short ID

    By default, a short ID consists of 12 lowercase letters or digits. This format is identical
    to the one used in the service-shortlink.

    """
    return generate(settings.SHORT_ID_ALPHABET, int(settings.SHORT_ID_SIZE))
