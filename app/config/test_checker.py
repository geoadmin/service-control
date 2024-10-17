from django.urls import reverse
from unittest import TestCase
from django.test import Client


class CheckerUrlTestCase(TestCase):

    def test_checker_url(self):
        client = Client()

        url = reverse('checker')

        response = client.get(url)
        assert response.status_code == 200
        content = response.json()

        assert 'success' in content
        assert 'message' in content
        assert content['success'] == True
        assert content['message'] == "OK"
