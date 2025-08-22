from unittest.mock import patch

from access.models import User
from pytest import fixture

from django.urls import reverse


@fixture(name="user")
def fixture_user(provider):
    with patch("access.models.Client") as client:
        client.return_value.create_user.return_value = True
        yield User.objects.create(
            username="dude",
            first_name="Jeffrey",
            last_name="Lebowski",
            email="dude@bowling.com",
            provider=provider,
        )


@patch("access.models.Client")
def test_disabled_users_are_displayed(cognito_client, client, admin_user, user):
    user.disable()

    client.force_login(admin_user)
    url = reverse("admin:access_user_changelist")
    response = client.get(url)
    assert b"Lebowski" in response.content


@patch("access.models.Client")
def test_disable_users(cognito_client, client, admin_user, user):
    cognito_client.return_value.disable_user.return_value = True

    client.force_login(admin_user)
    url = reverse("admin:access_user_changelist")
    response = client.post(
        url, data={"action": "disable", "_selected_action": [user.id]}
    )
    assert response.status_code == 302
    assert cognito_client.return_value.disable_user.called

    user.refresh_from_db()
    assert user.deleted_at


@patch("access.models.Client")
def test_delete_users(cognito_client, client, admin_user, user):
    cognito_client.return_value.delete_user.return_value = True

    client.force_login(admin_user)
    url = reverse("admin:access_user_changelist")
    response = client.post(
        url,
        data={
            "action": "delete_selected",
            "_selected_action": [user.id],
            "post": "yes",
        },
    )
    assert response.status_code == 302
    assert cognito_client.return_value.delete_user.called

    assert User.all_objects.first() is None


@patch("access.models.Client")
def test_user_id_and_deleted_at_readonly(
    cognito_client, client, admin_user, provider, user
):
    cognito_client.return_value.update_user.return_value = True

    client.force_login(admin_user)
    url = reverse("admin:access_user_change", args=[user.id])
    response = client.post(
        url,
        data={
            "username": "a",
            "user_id": "b",
            "first_name": "c",
            "last_name": "d",
            "email": "e@f.gh",
            "deleted_at_0": "2024-12-17",
            "deleted_at_1": "14:30:00",
            "provider": provider.id,
        },
    )
    assert response.status_code == 302
    assert cognito_client.return_value.update_user.called

    user.refresh_from_db()
    assert user.username == "a"
    assert user.user_id != "b"
    assert user.first_name == "c"
    assert user.last_name == "d"
    assert user.email == "e@f.gh"
    assert user.deleted_at is None
    assert user.provider == provider
