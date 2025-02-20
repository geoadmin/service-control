from unittest.mock import patch

from access.api import user_to_response
from access.models import User
from access.schemas import UserSchema
from botocore.exceptions import EndpointConnectionError
from pytest import fixture


@fixture(name='user')
def fixture_user(provider):
    with patch('access.models.Client') as client:
        client.return_value.create_user.return_value = True
        yield User.objects.create(
            username="dude",
            first_name="Jeffrey",
            last_name="Lebowski",
            email="dude@bowling.com",
            provider=provider
        )


def test_user_to_response_maps_fields_correctly(user):

    model = User.objects.last()

    actual = user_to_response(model)

    expected = UserSchema(
        username="dude",
        first_name="Jeffrey",
        last_name="Lebowski",
        email="dude@bowling.com",
        provider_id=user.provider.provider_id,
    )

    assert actual == expected


def test_get_user_returns_existing_user(user, django_user_factory, client):
    django_user_factory('test', 'test', [('access', 'user', 'view_user')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/users/dude")

    assert response.status_code == 200
    assert response.json() == {
        "username": "dude",
        "first_name": "Jeffrey",
        "last_name": "Lebowski",
        "email": "dude@bowling.com",
        "provider_id": "ch.bafu",
    }


def test_get_user_returns_404_if_nonexisting(user, django_user_factory, client):
    django_user_factory('test', 'test', [('access', 'user', 'view_user')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/users/nihilist")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}


def test_get_user_returns_401_if_not_logged_in(user, django_user_factory, client):
    response = client.get("/api/v1/users/dude")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_user_returns_403_if_no_permission(user, django_user_factory, client):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/users/dude")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


def test_get_users_returns_single_user(user, django_user_factory, client):
    django_user_factory('test', 'test', [('access', 'user', 'view_user')])
    client.login(username='test', password='test')

    response = client.get("/api/v1/users")

    assert response.status_code == 200
    assert response.json() == {
        "items": [{
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider_id": "ch.bafu",
        }]
    }


@patch('access.models.Client')
def test_get_users_returns_users_ordered_by_id(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.create_user.return_value = True

    django_user_factory('test', 'test', [('access', 'user', 'view_user')])
    client.login(username='test', password='test')

    model_fields = {
        "username": "veteran",
        "first_name": "Walter",
        "last_name": "Sobchak",
        "email": "veteran@bowling.com",
        "provider": user.provider,
    }
    User.objects.create(**model_fields)

    response = client.get("/api/v1/users")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "username": "dude",
                "first_name": "Jeffrey",
                "last_name": "Lebowski",
                "email": "dude@bowling.com",
                "provider_id": "ch.bafu",
            },
            {
                "username": "veteran",
                "first_name": "Walter",
                "last_name": "Sobchak",
                "email": "veteran@bowling.com",
                "provider_id": "ch.bafu",
            },
        ]
    }


def test_get_users_returns_401_if_not_logged_in(user, django_user_factory, client):
    response = client.get("/api/v1/users")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_get_users_returns_403_if_no_permission(user, django_user_factory, client):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.get("/api/v1/users")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


@patch('access.models.Client')
def test_post_users_creates_new_user_in_db_and_returns_it(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = True

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "donny",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": "donny@bowling.com",
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 201
    assert response.json() == payload
    assert User.objects.count() == 2
    assert cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_404_if_provider_id_does_not_exist(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "donny",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": "donny@bowling.com",
        "provider_id": "non_existing_provider_id",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}
    assert not cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_422_if_email_format_invalid(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    invalid_email = "donny_at_bowling_dot_com"
    payload = {
        "username": "donny",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": invalid_email,
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 422
    assert response.json() == {'code': 422, 'description': ["Enter a valid email address."]}
    assert not cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_409_if_user_exists_already(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "dude",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": "donny@bowling.com",
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 409
    assert response.json() == {
        'code': 409, 'description': ["User with this User name already exists."]
    }
    assert not cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_409_and_reports_all_errors_if_multiple_things_amiss(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    invalid_email = "donny_at_bowling_dot_com"
    payload = {
        "username": "dude",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": invalid_email,
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 409
    assert response.json() == {
        'code': 409,
        'description': ["Enter a valid email address.", "User with this User name already exists."]
    }
    assert not cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_500_if_cognito_inconsistent(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.create_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "donny",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": "donny@bowling.com",
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 500
    assert response.json() == {'code': 500, 'description': 'Internal Server Error'}
    assert User.objects.count() == 1
    assert cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_users_returns_503_if_cognito_down(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.create_user.side_effect = EndpointConnectionError(
        endpoint_url='http://localhost'
    )

    django_user_factory('test', 'test', [('access', 'user', 'add_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "donny",
        "first_name": "Theodore Donald",
        "last_name": "Kerabatsos",
        "email": "donny@bowling.com",
        "provider_id": "ch.bafu",
    }

    response = client.post("/api/v1/users", data=payload, content_type='application/json')

    assert response.status_code == 503
    assert response.json() == {'code': 503, 'description': 'Service Unavailable'}
    assert User.objects.count() == 1
    assert cognito_client.return_value.create_user.called


@patch('access.models.Client')
def test_post_user_returns_401_if_not_logged_in(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.create_user.return_value = True

    response = client.post("/api/v1/users", data={}, content_type='application/json')

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}
    assert not cognito_client.return_value.create_user.called
    assert User.objects.count() == 1


@patch('access.models.Client')
def test_post_user_returns_403_if_no_permission(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.create_user.return_value = True

    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.post("/api/v1/users", data={}, content_type='application/json')

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}
    assert not cognito_client.return_value.create_user.called
    assert User.objects.count() == 1


@patch('access.models.Client')
def test_delete_user_deletes_user(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.disable_user.return_value = True

    django_user_factory('test', 'test', [('access', 'user', 'delete_user')])
    client.login(username='test', password='test')

    response = client.delete("/api/v1/users/dude")

    assert response.status_code == 204
    assert response.content == b''
    assert User.objects.count() == 0
    assert cognito_client.return_value.disable_user.called


@patch('access.models.Client')
def test_delete_user_returns_404_if_nonexisting(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.disable_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'delete_user')])
    client.login(username='test', password='test')

    response = client.delete("/api/v1/users/lebowski")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}
    assert User.objects.count() == 1
    assert not cognito_client.return_value.disable_user.called


@patch('access.models.Client')
def test_delete_user_returns_500_if_cognito_inconsistent(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.disable_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'delete_user')])
    client.login(username='test', password='test')

    response = client.delete("/api/v1/users/dude")

    assert response.status_code == 500
    assert response.json() == {"code": 500, "description": "Internal Server Error"}
    assert User.objects.count() == 1
    assert cognito_client.return_value.disable_user.called


@patch('access.models.Client')
def test_delete_user_returns_503_if_cognito_down(cognito_client, user, django_user_factory, client):
    cognito_client.return_value.disable_user.side_effect = EndpointConnectionError(
        endpoint_url='http://localhost'
    )

    django_user_factory('test', 'test', [('access', 'user', 'delete_user')])
    client.login(username='test', password='test')

    response = client.delete("/api/v1/users/dude")

    assert response.status_code == 503
    assert response.json() == {"code": 503, "description": "Service Unavailable"}
    assert User.objects.count() == 1
    assert cognito_client.return_value.disable_user.called


@patch('access.models.Client')
def test_delete_user_returns_401_if_not_logged_in(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.disable_user.return_value = True

    response = client.delete("/api/v1/users/dude", data={}, content_type='application/json')

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}
    assert User.objects.count() == 1
    assert not cognito_client.return_value.disable_user.called


@patch('access.models.Client')
def test_delete_user_returns_403_if_no_permission(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.disable_user.return_value = True

    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.delete("/api/v1/users/dude", data={}, content_type='application/json')

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}
    assert User.objects.count() == 1
    assert not cognito_client.return_value.disable_user.called


def test_update_user_returns_401_if_not_logged_in(user, django_user_factory, client):
    response = client.put("/api/v1/users/dude")

    assert response.status_code == 401
    assert response.json() == {"code": 401, "description": "Unauthorized"}


def test_update_user_returns_403_if_no_permission(user, django_user_factory, client):
    django_user_factory('test', 'test', [])
    client.login(username='test', password='test')

    response = client.put("/api/v1/users/dude")

    assert response.status_code == 403
    assert response.json() == {"code": 403, "description": "Forbidden"}


@patch('access.models.Client')
def test_update_user_updates_existing_user_as_expected(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.update_user.return_value = True

    django_user_factory('test', 'test', [('access', 'user', 'change_user')])
    client.login(username='test', password='test')

    payload = {
        "username": "dude",
        "first_name": "Jeff",
        "last_name": "Bridges",
        "email": "tron@hollywood.com",
        "provider_id": "ch.bafu",
    }

    response = client.put("/api/v1/users/dude", data=payload, content_type='application/json')

    assert response.status_code == 200
    assert response.json() == payload

    user = User.objects.filter(username="dude").first()
    assert user.username == "dude"
    assert user.first_name == "Jeff"
    assert user.last_name == "Bridges"
    assert user.email == "tron@hollywood.com"
    assert user.provider.provider_id == "ch.bafu"

    assert cognito_client.return_value.update_user.called


def test_update_user_returns_404_and_leaves_user_as_is_if_user_nonexistent(
    user, django_user_factory, client
):

    django_user_factory('test', 'test', [('access', 'user', 'change_user')])
    client.login(username='test', password='test')

    user_before = User.objects.filter(username="dude").first()
    payload = {
        "username": "dude",
        "first_name": "Jeff",
        "last_name": "Bridges",
        "email": "tron@hollywood.com",
        "provider_id": "ch.bafu",
    }

    nonexistent_username = "maude"
    response = client.put(
        f"/api/v1/users/{nonexistent_username}", data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json() == {"code": 404, "description": "Resource not found"}
    user_after = User.objects.filter(username="dude").first()
    assert user_after == user_before


def test_update_user_returns_400_and_leaves_user_as_is_if_provider_nonexistent(
    user, django_user_factory, client
):

    django_user_factory('test', 'test', [('access', 'user', 'change_user')])
    client.login(username='test', password='test')

    user_before = User.objects.filter(username="dude").first()
    payload = {
        "username": "dude",
        "first_name": "Jeff",
        "last_name": "Bridges",
        "email": "tron@hollywood.com",
        "provider_id": "nonexistent_id",
    }

    response = client.put("/api/v1/users/dude", data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {"code": 400, "description": "Provider does not exist"}
    user_after = User.objects.filter(username="dude").first()
    assert user_after == user_before


@patch('access.models.Client')
def test_update_user_returns_500_and_leaves_user_as_is_if_cognito_inconsistent(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.update_user.return_value = False

    django_user_factory('test', 'test', [('access', 'user', 'change_user')])
    client.login(username='test', password='test')

    user_before = User.objects.filter(username="dude").first()
    payload = {
        "username": "dude",
        "first_name": "Jeff",
        "last_name": "Bridges",
        "email": "tron@hollywood.com",
        "provider_id": "ch.bafu",
    }

    response = client.put("/api/v1/users/dude", data=payload, content_type="application/json")

    assert response.status_code == 500
    assert response.json() == {"code": 500, "description": "Internal Server Error"}
    user_after = User.objects.filter(username="dude").first()
    assert user_after == user_before
    assert cognito_client.return_value.update_user.called


@patch('access.models.Client')
def test_update_user_returns_503_and_leaves_user_as_is_if_cognito_down(
    cognito_client, user, django_user_factory, client
):
    cognito_client.return_value.update_user.side_effect = EndpointConnectionError(
        endpoint_url='http://localhost'
    )

    django_user_factory('test', 'test', [('access', 'user', 'change_user')])
    client.login(username='test', password='test')

    user_before = User.objects.filter(username="dude").first()
    payload = {
        "username": "dude",
        "first_name": "Jeff",
        "last_name": "Bridges",
        "email": "tron@hollywood.com",
        "provider_id": "ch.bafu",
    }

    response = client.put("/api/v1/users/dude", data=payload, content_type="application/json")

    assert response.status_code == 503
    assert response.json() == {"code": 503, "description": "Service Unavailable"}
    user_after = User.objects.filter(username="dude").first()
    assert user_after == user_before
    assert cognito_client.return_value.update_user.called
