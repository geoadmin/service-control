from unittest.mock import call
from unittest.mock import patch

from cognito.utils.client import Client

from django.test import TestCase


class ClientTestCase(TestCase):

    @patch('cognito.utils.client.client')
    def test_get_users(self, boto3):
        client = Client()
        client.get_users()
        self.assertIn(call().list_users(UserPoolId=client.user_pool_id), boto3.mock_calls)

    @patch('cognito.utils.client.client')
    def test_get_user(self, boto3):
        client = Client()
        client.get_user('1234')
        self.assertIn(
            call().admin_get_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_create_user(self, boto3):
        client = Client()
        client.create_user('1234', 'test@example.org')
        self.assertIn(
            call().admin_create_user(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }],
                DesiredDeliveryMediums=['EMAIL']
            ),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_delete_user(self, boto3):
        client = Client()
        client.delete_user('1234')
        self.assertIn(
            call().admin_delete_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_update_user(self, boto3):
        client = Client()
        client.update_user('1234', 'test@example.org')
        self.assertIn(
            call().admin_update_user_attributes(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }]
            ),
            boto3.mock_calls
        )
