import pytest
from access.models import User
from provider.models import Provider


@pytest.mark.django_db
class TestUser:

    def test_user_stored_as_expected_for_valid_input(self):
        provider = Provider.objects.create()
        model_fields = {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider": provider,
        }

        actual = User.objects.create(**model_fields)

        assert actual.username == "dude"
        assert actual.first_name == "Jeffrey"
        assert actual.last_name == "Lebowski"
        assert actual.email == "dude@bowling.com"
        assert actual.provider == provider

    def test_user_stores_user_even_with_invalid_email(self):
        # Demonstrates that an EmailField only ensures form validation, not model validation.
        provider = Provider.objects.create()
        model_fields = {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude_at_bowling_dot_com",
            "provider": provider,
        }

        actual = User.objects.create(**model_fields)

        assert actual.username == "dude"
        assert actual.first_name == "Jeffrey"
        assert actual.last_name == "Lebowski"
        assert actual.email == "dude_at_bowling_dot_com"
        assert actual.provider == provider
