from access.api import router
from access.api import user_to_response
from access.models import User
from ninja.testing import TestClient
from access.schemas import UserSchema
from provider.models import Provider

from django.test import TestCase


class ApiTestCase(TestCase):

    def setUp(self):
        provider = Provider.objects.create()
        model_fields = {
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
            id=model.id,
            first_name="Jeffrey",
            last_name="Lebowski",
            email="dude@bowling.com",
            provider_id=Provider.objects.last().id,
        )

        assert actual == expected

    def test_get_user_returns_existing_user(self):

        user_id = User.objects.last().id

        client = TestClient(router)
        response = client.get(f"/{user_id}")

        assert response.status_code == 200
        assert response.data == {
            "id": user_id,
            "first_name": "Jeffrey",
            "last_name": "Lebowski",
            "email": "dude@bowling.com",
            "provider_id": Provider.objects.last().id,
        }

    def test_get_user_returns_404_if_nonexisting(self):

        client = TestClient(router)
        response = client.get("/2")

        assert response.status_code == 404
        assert response.data == {"detail": "Not Found"}
