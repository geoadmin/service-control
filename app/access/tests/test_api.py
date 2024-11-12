from unittest.mock import patch

from access.api import user_to_response
from access.models import User
from access.schemas import UserSchema
from botocore.exceptions import EndpointConnectionError
from provider.models import Provider
from utils.testing import create_user_with_permissions

from django.test import TestCase


# pylint: disable=too-many-public-methods
class ApiTestCase(TestCase):

    def setUp(self):
        provider = Provider.objects.create()
        model_fields = {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider": provider,
        }
        User.objects.create(**model_fields)

    def test_user_to_response_maps_fields_correctly(self):

        model = User.objects.last()

        actual = user_to_response(model)

        expected = UserSchema(
            username="dude",
            first_name="Jeffrey",
            last_name="Lebowski",
            email="dude@bowling.com",
            provider_id=Provider.objects.last().id,
        )

        assert actual == expected

    def test_get_user_returns_existing_user(self):
        create_user_with_permissions('test', 'test', [('access', 'user', 'view_user')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/users/dude")

        assert response.status_code == 200
        assert response.json() == {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

    def test_get_user_returns_404_if_nonexisting(self):
        create_user_with_permissions('test', 'test', [('access', 'user', 'view_user')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/users/nihilist")

        assert response.status_code == 404
        assert response.json() == {"code": 404, "description": "Resource not found"}

    def test_get_user_returns_401_if_not_logged_in(self):
        response = self.client.get("/api/users/dude")

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}

    def test_get_user_returns_403_if_no_permission(self):
        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/users/dude")

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}

    def test_get_users_returns_single_user(self):
        create_user_with_permissions('test', 'test', [('access', 'user', 'view_user')])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/users")

        assert response.status_code == 200
        assert response.json() == {
            "items": [{
                "username": "dude",
                "first_name": "Jeffrey",
                "last_name": "Lebowski",
                "email": "dude@bowling.com",
                "provider_id": Provider.objects.last().id,
            }]
        }

    def test_get_users_returns_users_ordered_by_id(self):
        create_user_with_permissions('test', 'test', [('access', 'user', 'view_user')])
        self.client.login(username='test', password='test')

        model_fields = {
            "username": "veteran",
            "first_name": "Walter",
            "last_name": "Sobchak",
            "email": "veteran@bowling.com",
            "provider": Provider.objects.last(),
        }
        User.objects.create(**model_fields)

        response = self.client.get("/api/users")

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "username": "dude",
                    "first_name": "Jeffrey",
                    "last_name": "Lebowski",
                    "email": "dude@bowling.com",
                    "provider_id": Provider.objects.last().id,
                },
                {
                    "username": "veteran",
                    "first_name": "Walter",
                    "last_name": "Sobchak",
                    "email": "veteran@bowling.com",
                    "provider_id": Provider.objects.last().id,
                },
            ]
        }

    def test_get_users_returns_401_if_not_logged_in(self):
        response = self.client.get("/api/users")

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}

    def test_get_users_returns_403_if_no_permission(self):
        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.get("/api/users")

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}

    @patch('access.api.create_cognito_user')
    def test_post_users_creates_new_user_in_db_and_returns_it(self, create_cognito_user):
        create_cognito_user.return_value = True

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 201
        assert response.json() == payload
        assert User.objects.count() == 2
        assert create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_404_if_provider_id_does_not_exist(self, create_cognito_user):
        create_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        non_existing_provider_id = Provider.objects.last().id + 1
        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": non_existing_provider_id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 404
        assert response.json() == {"code": 404, "description": "Resource not found"}
        assert not create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_422_if_email_format_invalid(self, create_cognito_user):
        create_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        invalid_email = "donny_at_bowling_dot_com"
        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": invalid_email,
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 422
        assert response.json() == {'code': 422, 'description': ["Enter a valid email address."]}
        assert not create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_409_if_user_exists_already(self, create_cognito_user):
        create_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        payload = {
            "username": "dude",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 409
        assert response.json() == {
            'code': 409, 'description': ["User with this User name already exists."]
        }
        assert not create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_409_and_reports_all_errors_if_multiple_things_amiss(
        self, create_cognito_user
    ):
        create_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        invalid_email = "donny_at_bowling_dot_com"
        payload = {
            "username": "dude",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": invalid_email,
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 409
        assert response.json() == {
            'code': 409,
            'description': [
                "Enter a valid email address.", "User with this User name already exists."
            ]
        }
        assert not create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_500_if_cognito_inconsistent(self, create_cognito_user):
        create_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 500
        assert response.json() == {'code': 500, 'description': 'Internal Server Error'}
        assert User.objects.count() == 1
        assert create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_users_returns_503_if_cognito_down(self, create_cognito_user):
        create_cognito_user.side_effect = EndpointConnectionError(endpoint_url='http://localhost')

        create_user_with_permissions('test', 'test', [('access', 'user', 'add_user')])
        self.client.login(username='test', password='test')

        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("/api/users", data=payload, content_type='application/json')

        assert response.status_code == 503
        assert response.json() == {'code': 503, 'description': 'Service Unavailable'}
        assert User.objects.count() == 1
        assert create_cognito_user.called

    @patch('access.api.create_cognito_user')
    def test_post_user_returns_401_if_not_logged_in(self, create_cognito_user):
        create_cognito_user.return_value = True

        response = self.client.post("/api/users", data={}, content_type='application/json')

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}
        assert not create_cognito_user.called
        assert User.objects.count() == 1

    @patch('access.api.create_cognito_user')
    def test_post_user_returns_403_if_no_permission(self, create_cognito_user):
        create_cognito_user.return_value = True

        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.post("/api/users", data={}, content_type='application/json')

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}
        assert not create_cognito_user.called
        assert User.objects.count() == 1

    @patch('access.api.disable_cognito_user')
    def test_delete_user_deletes_user(self, disable_cognito_user):
        disable_cognito_user.return_value = True

        create_user_with_permissions('test', 'test', [('access', 'user', 'delete_user')])
        self.client.login(username='test', password='test')

        response = self.client.delete("/api/users/dude")

        assert response.status_code == 204
        assert response.content == b''
        assert User.objects.count() == 0
        assert disable_cognito_user.called

    @patch('access.api.disable_cognito_user')
    def test_delete_user_returns_404_if_nonexisting(self, disable_cognito_user):
        disable_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'delete_user')])
        self.client.login(username='test', password='test')

        response = self.client.delete("/api/users/lebowski")

        assert response.status_code == 404
        assert response.json() == {"code": 404, "description": "Resource not found"}
        assert User.objects.count() == 1
        assert not disable_cognito_user.called

    @patch('access.api.disable_cognito_user')
    def test_delete_user_returns_500_if_cognito_inconsistent(self, disable_cognito_user):
        disable_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'delete_user')])
        self.client.login(username='test', password='test')

        response = self.client.delete("/api/users/dude")

        assert response.status_code == 500
        assert response.json() == {"code": 500, "description": "Internal Server Error"}
        assert User.objects.count() == 1
        assert disable_cognito_user.called

    @patch('access.api.disable_cognito_user')
    def test_delete_user_returns_503_if_cognito_down(self, disable_cognito_user):
        disable_cognito_user.side_effect = EndpointConnectionError(endpoint_url='http://localhost')

        create_user_with_permissions('test', 'test', [('access', 'user', 'delete_user')])
        self.client.login(username='test', password='test')

        response = self.client.delete("/api/users/dude")

        assert response.status_code == 503
        assert response.json() == {"code": 503, "description": "Service Unavailable"}
        assert User.objects.count() == 1
        assert disable_cognito_user.called

    @patch('access.api.disable_cognito_user')
    def test_delete_user_returns_401_if_not_logged_in(self, disable_cognito_user):
        disable_cognito_user.return_value = True

        response = self.client.delete("/api/users/dude", data={}, content_type='application/json')

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}
        assert User.objects.count() == 1
        assert not disable_cognito_user.called

    @patch('access.api.disable_cognito_user')
    def test_delete_user_returns_403_if_no_permission(self, disable_cognito_user):
        disable_cognito_user.return_value = True

        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.delete("/api/users/dude", data={}, content_type='application/json')

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}
        assert User.objects.count() == 1
        assert not disable_cognito_user.called

    def test_update_user_returns_401_if_not_logged_in(self):
        response = self.client.put("/api/users/dude")

        assert response.status_code == 401
        assert response.json() == {"code": 401, "description": "Unauthorized"}

    def test_update_user_returns_403_if_no_permission(self):
        create_user_with_permissions('test', 'test', [])
        self.client.login(username='test', password='test')

        response = self.client.put("/api/users/dude")

        assert response.status_code == 403
        assert response.json() == {"code": 403, "description": "Forbidden"}

    @patch('access.api.update_cognito_user')
    def test_update_user_updates_existing_user_as_expected(self, update_cognito_user):
        update_cognito_user.return_value = True

        create_user_with_permissions('test', 'test', [('access', 'user', 'change_user')])
        self.client.login(username='test', password='test')

        payload = {
            "username": "dude",
            "first_name": "Jeff",
            "last_name": "Bridges",
            "email": "tron@hollywood.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.put("/api/users/dude", data=payload, content_type='application/json')

        assert response.status_code == 200
        assert response.json() == payload
        user = User.objects.filter(username="dude").first()
        for key, value in payload.items():
            assert getattr(user, key) == value
        assert update_cognito_user.called

    def test_update_user_returns_404_and_leaves_user_as_is_if_user_nonexistent(self):

        create_user_with_permissions('test', 'test', [('access', 'user', 'change_user')])
        self.client.login(username='test', password='test')

        user_before = User.objects.filter(username="dude").first()
        payload = {
            "username": "dude",
            "first_name": "Jeff",
            "last_name": "Bridges",
            "email": "tron@hollywood.com",
            "provider_id": Provider.objects.last().id,
        }

        nonexistent_username = "maude"
        response = self.client.put(
            f"/api/users/{nonexistent_username}", data=payload, content_type='application/json'
        )

        assert response.status_code == 404
        assert response.json() == {"code": 404, "description": "Resource not found"}
        user_after = User.objects.filter(username="dude").first()
        assert user_after == user_before

    def test_update_user_returns_400_and_leaves_user_as_is_if_provider_nonexistent(self):

        create_user_with_permissions('test', 'test', [('access', 'user', 'change_user')])
        self.client.login(username='test', password='test')

        user_before = User.objects.filter(username="dude").first()
        nonexistent_id = Provider.objects.last().id + 1234
        payload = {
            "username": "dude",
            "first_name": "Jeff",
            "last_name": "Bridges",
            "email": "tron@hollywood.com",
            "provider_id": nonexistent_id,
        }

        response = self.client.put("/api/users/dude", data=payload, content_type="application/json")

        assert response.status_code == 400
        assert response.json() == {"code": 400, "description": "Provider does not exist"}
        user_after = User.objects.filter(username="dude").first()
        assert user_after == user_before

    @patch('access.api.update_cognito_user')
    def test_update_user_returns_500_and_leaves_user_as_is_if_cognito_inconsistent(
        self, update_cognito_user
    ):
        update_cognito_user.return_value = False

        create_user_with_permissions('test', 'test', [('access', 'user', 'change_user')])
        self.client.login(username='test', password='test')

        user_before = User.objects.filter(username="dude").first()
        payload = {
            "username": "dude",
            "first_name": "Jeff",
            "last_name": "Bridges",
            "email": "tron@hollywood.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.put("/api/users/dude", data=payload, content_type="application/json")

        assert response.status_code == 500
        assert response.json() == {"code": 500, "description": "Internal Server Error"}
        user_after = User.objects.filter(username="dude").first()
        assert user_after == user_before
        assert update_cognito_user.called

    @patch('access.api.update_cognito_user')
    def test_update_user_returns_503_and_leaves_user_as_is_if_cognito_down(
        self, update_cognito_user
    ):
        update_cognito_user.side_effect = EndpointConnectionError(endpoint_url='http://localhost')

        create_user_with_permissions('test', 'test', [('access', 'user', 'change_user')])
        self.client.login(username='test', password='test')

        user_before = User.objects.filter(username="dude").first()
        payload = {
            "username": "dude",
            "first_name": "Jeff",
            "last_name": "Bridges",
            "email": "tron@hollywood.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.put("/api/users/dude", data=payload, content_type="application/json")

        assert response.status_code == 503
        assert response.json() == {"code": 503, "description": "Service Unavailable"}
        user_after = User.objects.filter(username="dude").first()
        assert user_after == user_before
        assert update_cognito_user.called
