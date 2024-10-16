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

        client = TestClient(router)
        response = client.get("users/dude")

        assert response.status_code == 200
        assert response.data == {
            "username": "dude",
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

    def test_get_user_returns_404_if_nonexisting(self):

        client = TestClient(router)
        response = client.get("users/nihilist")

        assert response.status_code == 404
        assert response.data == {"detail": "Not Found"}

    def test_get_users_returns_single_user(self):

        client = TestClient(router)
        response = client.get("users")

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

        client = TestClient(router)
        response = client.get("users")

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
