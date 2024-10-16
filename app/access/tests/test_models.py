import pytest
from access.models import User
from provider.models import Provider

from django.core.exceptions import ValidationError
from django.forms import ModelForm


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

    def test_user_with_invalid_email_raises_exception_when_creating_db_record(self):
        provider = Provider.objects.create()
        model_fields = {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude_at_bowling_dot_com",
            "provider": provider,
        }

        with pytest.raises(ValidationError):
            User.objects.create(**model_fields)

    def test_form_invalid_for_user_with_invalid_email(self):

        class UserForm(ModelForm):

            class Meta:
                model = User
                fields = "__all__"

        provider = Provider.objects.create()
        data = {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude_at_bowling_dot_com",
            "provider": provider,
        }
        form = UserForm(data)

        assert not form.is_valid()
