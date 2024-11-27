from django.core.validators import RegexValidator
from django.db import models
from django.utils.regex_helper import _lazy_re_compile

slug_re = _lazy_re_compile(r"^[-a-z0-9_.]+\Z")


class CustomSlugField(models.CharField):  # type:ignore[type-arg]
    """A custom slug field also allowing periods but not uppercase letters."""

    default_validators = [
        RegexValidator(
            slug_re,
            "Enter a valid “slug” consisting of lowercase letters, numbers, underscores, hyphens"
            " and periods.",
            "invalid",
        )
    ]
