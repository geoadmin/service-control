from access.api import router
from access.api import user_to_response
from access.models import User
from access.schemas import UserSchema
from ninja.testing import TestClient
from provider.models import Provider

from django.test import TestCase


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

        self.client = TestClient(router)

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

        response = self.client.get("users/dude")

        assert response.status_code == 200
        assert response.data == {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

    def test_get_user_returns_404_if_nonexisting(self):

        response = self.client.get("users/nihilist")

        assert response.status_code == 404
        assert response.data == {"detail": "Not Found"}

    def test_get_users_returns_single_user(self):

        response = self.client.get("users")

        assert response.status_code == 200
        assert response.data == {
            "items": [{
                "username": "dude",
                "first_name": "Jeffrey",
                "last_name": "Lebowski",
                "email": "dude@bowling.com",
                "provider_id": Provider.objects.last().id,
            }]
        }

    def test_get_users_returns_users_ordered_by_id(self):

        model_fields = {
            "username": "veteran",
            "first_name": "Walter",
            "last_name": "Sobchak",
            "email": "veteran@bowling.com",
            "provider": Provider.objects.last(),
        }
        User.objects.create(**model_fields)

        response = self.client.get("users")

        assert response.status_code == 200
        assert response.data == {
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

    def test_post_users_creates_new_user_in_db_and_returns_it(self):

        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("users", json=payload)

        assert response.status_code == 201
        assert response.data == payload

    def test_post_users_returns_404_if_provider_id_does_not_exist(self):

        non_existing_provider_id = Provider.objects.last().id + 1
        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": non_existing_provider_id,
        }

        response = self.client.post("users", json=payload)

        assert response.status_code == 404

    def test_post_users_returns_422_if_email_format_invalid(self):

        invalid_email = "donny_at_bowling_dot_com"
        payload = {
            "username": "donny",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": invalid_email,
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("users", json=payload)

        assert response.status_code == 422
        assert response.data == {'detail': "['Enter a valid email address.']"}

    def test_post_users_returns_409_if_user_exists_already(self):

        payload = {
            "username": "dude",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": "donny@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("users", json=payload)

        assert response.status_code == 409
        assert response.data == {'detail': "['User with this User name already exists.']"}

    def test_post_users_returns_409_and_reports_all_errors_if_multiple_things_amiss(self):

        invalid_email = "donny_at_bowling_dot_com"
        payload = {
            "username": "dude",
            "first_name": "Theodore Donald",
            "last_name": "Kerabatsos",
            "email": invalid_email,
            "provider_id": Provider.objects.last().id,
        }

        response = self.client.post("users", json=payload)

        assert response.status_code == 409
        assert response.data == {
            'detail': "['Enter a valid email address.', 'User with this User name already exists.']"
        }
