from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command


@patch.dict(
    "os.environ",
    {
        "DJANGO_SUPERUSER_USERNAME": "admin",
        "DJANGO_SUPERUSER_EMAIL": "admin@admin.ch",
        "DJANGO_SUPERUSER_PASSWORD": "very-secure",
    },
)
def test_command_creates(db):
    out = StringIO()
    call_command("manage_superuser", verbosity=2, stdout=out)
    assert "Created the superuser admin" in out.getvalue()

    user = get_user_model().objects.filter(username="admin").first()
    assert user
    assert user.email == "admin@admin.ch"
    assert user.check_password("very-secure")
    assert user.is_staff
    assert user.is_superuser


@patch.dict(
    "os.environ",
    {
        "DJANGO_SUPERUSER_USERNAME": "admin",
        "DJANGO_SUPERUSER_EMAIL": "admin@admin.ch",
        "DJANGO_SUPERUSER_PASSWORD": "very-secure",
    },
)
def test_command_updates(db):
    user = get_user_model().objects.create(
        username="admin", email="amdin@amdin.ch", is_staff=False, is_superuser=False
    )
    user.set_password("not-secure")

    out = StringIO()
    call_command("manage_superuser", verbosity=2, stdout=out)
    assert "Updated the superuser admin" in out.getvalue()

    user = get_user_model().objects.filter(username="admin").first()
    assert user
    assert user.email == "admin@admin.ch"
    assert user.check_password("very-secure")
    assert user.is_staff
    assert user.is_superuser


def test_fails_if_undefined(db):
    out = StringIO()
    call_command("manage_superuser", stderr=out)
    assert "Environment variables not set or empty" in out.getvalue()
    assert get_user_model().objects.count() == 0


@patch.dict(
    "os.environ",
    {
        "DJANGO_SUPERUSER_USERNAME": "",
        "DJANGO_SUPERUSER_EMAIL": "",
        "DJANGO_SUPERUSER_PASSWORD": "",
    },
)
def test_fails_if_empty(db):
    out = StringIO()
    call_command("manage_superuser", stderr=out)
    assert "Environment variables not set or empty" in out.getvalue()
    assert get_user_model().objects.count() == 0
