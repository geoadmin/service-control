from config.api import api_root
from ninja.testing import TestClient

from django.test import TestCase


class CheckerUrlTestCase(TestCase):

    def test_checker_url(self):
        client = TestClient(api_root)

        # intentionally not using reverse here as we want to
        # make sure the URL really is /checker
        url = '/checker'

        response = client.get(url)
        assert response.status_code == 200
        content = response.json()

        assert 'success' in content
        assert 'message' in content
        assert content['success'] is True
        assert content['message'] == "OK"
