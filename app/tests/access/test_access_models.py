from unittest.mock import call
from unittest.mock import patch

from access.models import CognitoInconsistencyError
from access.models import User
from provider.models import Provider
from pytest import fixture
from pytest import raises

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone


@fixture(name='provider')
def fixture_provider(db):
    yield Provider.objects.create(
        slug="ch.bafu",
        acronym_de="BAFU",
        acronym_fr="OFEV",
        acronym_en="FOEN",
        name_de="Bundesamt für Umwelt",
        name_fr="Office fédéral de l'environnement",
        name_en="Federal Office for the Environment"
    )


@patch('access.models.Client')
def test_user_stored_as_expected_for_valid_input(client, provider):
    client.return_value.create_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert len(actual.user_id) == 12
    assert actual.username == "dude"
    assert actual.first_name == "Jeffrey"
    assert actual.last_name == "Lebowski"
    assert actual.email == "dude@bowling.com"
    assert actual.provider == provider
    assert client.return_value.create_user.called


@patch('access.models.Client')
def test_user_raises_exception_for_user_with_existing_user_name(client, provider):
    client.return_value.create_user.return_value = True

    User.objects.create(
        username="dude",
        first_name="Jeffrey",
        last_name="Lebowski",
        email="dude@bowling.com",
        provider=provider
    )
    with raises(ValidationError):
        User.objects.create(
            username="dude",
            first_name="XXX",
            last_name="YYY",
            email="xxx@yyy.com",
            provider=provider
        )

    assert User.objects.count() == 1
    assert client.return_value.create_user.call_count == 1


@patch('access.models.Client')
def test_user_with_invalid_email_raises_exception_when_creating_db_record(client, provider):
    client.return_value.create_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude_at_bowling_dot_com",
        "provider": provider,
    }

    with raises(ValidationError):
        User.objects.create(**model_fields)

    assert User.objects.count() == 0
    assert not client.return_value.create_user.called


@patch('access.models.Client')
@patch('access.models.logger')
def test_create_user_raises_cognito_exception(logger, client, provider):
    client.return_value.create_user.return_value = False

    model_fields = {
        "user_id": "2ihg2ox304po",
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    with raises(CognitoInconsistencyError):
        User.objects.create(**model_fields)

    assert User.objects.count() == 0
    assert client.return_value.create_user.called
    assert call.critical(
        'User %s already exists in cognito, not created', '2ihg2ox304po'
    ) in logger.mock_calls


@patch('access.models.Client')
def test_save_user_updates_records(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.update_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert actual.email == "dude@bowling.com"
    assert client.return_value.create_user.called

    actual.email = "jeffrey.lebowski@bowling.com"
    actual.save()

    updated = User.objects.first()

    assert updated.email == 'jeffrey.lebowski@bowling.com'
    assert client.return_value.update_user.called


@patch('access.models.Client')
def test_save_disabled_user_updates_records(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.update_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
        "deleted_at": timezone.now()
    }

    User.objects.create(**model_fields)
    actual = User.all_objects.first()

    assert actual.email == "dude@bowling.com"
    assert client.return_value.create_user.called

    actual.email = "jeffrey.lebowski@bowling.com"
    actual.save()

    updated = User.all_objects.first()

    assert updated.email == 'jeffrey.lebowski@bowling.com'
    assert client.return_value.update_user.called


@patch('access.models.Client')
def test_save_user_raises_cognito_exception(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.update_user.return_value = False

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert actual.email == "dude@bowling.com"
    assert client.return_value.create_user.called

    actual.email = "jeffrey.lebowski@bowling.com"
    with raises(CognitoInconsistencyError):
        actual.save()

    retained = User.objects.first()

    assert retained.email == 'dude@bowling.com'
    assert client.return_value.update_user.called


@patch('access.models.Client')
def test_delete_user_deletes_records(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.delete_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert client.return_value.create_user.called

    actual.delete()

    assert not User.objects.first()
    assert client.return_value.delete_user.called


@patch('access.models.Client')
def test_delete_disabled_user_deletes_records(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.delete_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
        "deleted_at": timezone.now()
    }

    User.objects.create(**model_fields)
    actual = User.all_objects.first()

    assert client.return_value.create_user.called

    actual.delete()

    assert not User.all_objects.first()
    assert client.return_value.delete_user.called


@patch('access.models.Client')
def test_delete_user_raises_cognito_exception(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.delete_user.return_value = False

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert client.return_value.create_user.called

    with raises(CognitoInconsistencyError):
        actual.delete()

    assert User.objects.first()
    assert client.return_value.delete_user.called


@patch('access.models.Client')
def test_disable_user_disables_records(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.disable_user.return_value = True

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert client.return_value.create_user.called

    actual.disable()

    assert not User.objects.first()
    assert User.all_objects.first()
    assert client.return_value.disable_user.called


@patch('access.models.Client')
def test_disable_user_raises_cognito_exception(client, provider):
    client.return_value.create_user.return_value = True
    client.return_value.disable_user.return_value = False

    model_fields = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider": provider,
    }

    User.objects.create(**model_fields)
    actual = User.objects.first()

    assert client.return_value.create_user.called

    with raises(CognitoInconsistencyError):
        actual.disable()

    assert User.objects.first()
    assert client.return_value.disable_user.called


@patch('access.models.Client')
def test_form_invalid_for_user_with_invalid_email(client, provider):
    client.return_value.create_user.return_value = True

    class UserForm(ModelForm):

        class Meta:
            model = User
            fields = "__all__"

    data = {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude_at_bowling_dot_com",
        "provider": provider,
    }
    form = UserForm(data)

    assert not form.is_valid()
