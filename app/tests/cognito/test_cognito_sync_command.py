from io import StringIO
from unittest.mock import call
from unittest.mock import patch

from access.models import User
from pytest import fixture

from django.core.management import call_command
from django.utils import timezone


@fixture(name="user")
def fixture_user(provider):
    with patch("access.models.Client") as client:
        client.return_value.create_user.return_value = True
        yield User.objects.create(
            user_id="2ihg2ox304po",
            username="1",
            first_name="1",
            last_name="1",
            email="1@example.org",
            provider=provider,
        )


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_adds(cognito_client, user):
    cognito_client.return_value.list_users.return_value = []

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "adding user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) added" in out.getvalue()
    assert (
        call().create_user("2ihg2ox304po", "1", "1@example.org")
        in cognito_client.mock_calls
    )


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_deletes(cognito_client, db, cognito_user_response_factory):
    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org")
    ]

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "deleting user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) deleted" in out.getvalue()
    assert call().delete_user("2ihg2ox304po") in cognito_client.mock_calls


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_updates(cognito_client, user, cognito_user_response_factory):
    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "2@example.org")
    ]

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "updating user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) updated" in out.getvalue()
    assert (
        call().update_user("2ihg2ox304po", "1", "1@example.org")
        in cognito_client.mock_calls
    )


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_updates_disabled(cognito_client, user, cognito_user_response_factory):
    user.deleted_at = timezone.now()
    user.save()
    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org")
    ]

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "disabling user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) disabled" in out.getvalue()
    assert call().disable_user("2ihg2ox304po") in cognito_client.mock_calls


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_updates_enabled(cognito_client, user, cognito_user_response_factory):
    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org", False)
    ]

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "enabling user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) enabled" in out.getvalue()
    assert call().enable_user("2ihg2ox304po") in cognito_client.mock_calls


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_does_not_updates_if_unchanged(
    cognito_client, user, cognito_user_response_factory
):
    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org")
    ]

    out = StringIO()
    call_command("cognito_sync", verbosity=2, stdout=out)

    assert "nothing to be done" in out.getvalue()


@patch("builtins.input")
@patch("cognito.management.commands.cognito_sync.Client")
def test_command_clears_if_confirmed(
    cognito_client, input_, user, cognito_user_response_factory
):
    input_.side_effect = ["yes"]
    cognito_client.return_value.list_users.side_effect = [
        [cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org")],
        [],
    ]

    out = StringIO()
    call_command("cognito_sync", clear=True, verbosity=2, stdout=out)

    assert "This action will delete all managed users from cognito" in out.getvalue()
    assert "deleting user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) deleted" in out.getvalue()
    assert "adding user 2ihg2ox304po" in out.getvalue()
    assert "1 user(s) added" in out.getvalue()
    assert call().delete_user("2ihg2ox304po") in cognito_client.mock_calls
    assert (
        call().create_user("2ihg2ox304po", "1", "1@example.org")
        in cognito_client.mock_calls
    )


@patch("builtins.input")
@patch("cognito.management.commands.cognito_sync.Client")
def test_command_does_not_clears_if_not_confirmed(
    cognito_client, input_, user, cognito_user_response_factory
):
    input_.side_effect = ["no"]
    cognito_client.return_value.list_users.side_effect = [
        [cognito_user_response_factory("2ihg2ox304po", "1", "1@example.org")],
        [],
    ]

    out = StringIO()
    call_command("cognito_sync", clear=True, verbosity=2, stdout=out)

    assert "This action will delete all managed users from cognito" in out.getvalue()
    assert "operation cancelled" in out.getvalue()
    assert call().delete_user("1") not in cognito_client.mock_calls
    assert call().create_user("1", "1@example.org") not in cognito_client.mock_calls


@patch("cognito.management.commands.cognito_sync.Client")
def test_command_runs_dry(
    cognito_client, provider, user, cognito_user_response_factory
):
    User.objects.create(
        user_id="goho4o3ggg2o",
        username="2",
        first_name="2",
        last_name="2",
        email="2@example.org",
        provider=provider,
    )

    cognito_client.return_value.list_users.return_value = [
        cognito_user_response_factory("2ihg2ox304po", "1", "10@example.org"),
        cognito_user_response_factory("04i4p3g4iggh", "3", "3@example.org"),
    ]

    out = StringIO()
    call_command("cognito_sync", dry_run=True, verbosity=2, stdout=out)

    assert "adding user goho4o3ggg2o" in out.getvalue()
    assert "deleting user 04i4p3g4iggh" in out.getvalue()
    assert "updating user 2ihg2ox304po" in out.getvalue()
    assert "dry run" in out.getvalue()
    assert cognito_client.return_value.list_users.called
    assert not cognito_client.return_value.create_user.called
    assert not cognito_client.return_value.delete_user.called
    assert not cognito_client.return_value.update_user.called
