from unittest.mock import call
from unittest.mock import patch

from cognito.utils.client import Client
from cognito.utils.client import user_attributes_to_dict

from django.test import TestCase


def cognito_user(username, managed):
    if managed:
        return {
            'Username': username,
            'Attributes': [{
                'Name': 'email', 'Value': 'test@example.org'
            }, {
                'Name': 'custom:managed', 'Value': 'True'
            }]
        }
    return {'Username': username, 'Attributes': [{'Name': 'email', 'Value': 'test@example.org'}]}


class ClientTestCase(TestCase):

    def test_user_attributes_to_dict(self):
        attributes = user_attributes_to_dict({
            'UserAttributes': [{
                'Name': 'email', 'Value': 'test@example.org'
            }, {
                'Name': 'custom:managed', 'Value': 'True'
            }]
        })
        self.assertEqual(attributes, {'email': 'test@example.org', 'custom:managed': 'True'})

        attributes = user_attributes_to_dict({
            'Attributes': [{
                'Name': 'email', 'Value': 'test@example.org'
            }, {
                'Name': 'custom:managed', 'Value': 'True'
            }]
        })
        self.assertEqual(attributes, {'email': 'test@example.org', 'custom:managed': 'True'})

    @patch('cognito.utils.client.client')
    def test_list_users_returns_only_managed(self, boto3):
        managed = {'Username': '1234', 'Attributes': [{'Name': 'custom:managed', 'Value': 'True'}]}
        unmanaged = {'Username': '5678'}
        boto3.return_value.list_users.return_value = {'Users': [managed, unmanaged]}

        client = Client()
        users = client.list_users()
        self.assertEqual(users, [managed])
        self.assertIn(call().list_users(UserPoolId=client.user_pool_id, Limit=60), boto3.mock_calls)

    @patch('cognito.utils.client.client')
    def test_list_users_pagination(self, boto3):
        users = [cognito_user(str(count), True) for count in range(1, 131)]
        response_1 = {'Users': users[0:60], 'PaginationToken': '1'}
        response_2 = {'Users': users[60:120], 'PaginationToken': '2'}
        response_3 = {'Users': users[120:130]}
        boto3.return_value.list_users.side_effect = [response_1, response_2, response_3]

        client = Client()
        users = client.list_users()

        self.assertEqual([user['Username'] for user in users], [str(x) for x in range(1, 131)])
        self.assertIn(call().list_users(UserPoolId=client.user_pool_id, Limit=60), boto3.mock_calls)
        self.assertIn(
            call().list_users(UserPoolId=client.user_pool_id, Limit=60, PaginationToken='2'),
            boto3.mock_calls
        )
        self.assertIn(
            call().list_users(UserPoolId=client.user_pool_id, Limit=60, PaginationToken='2'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_get_user_returns_managed(self, boto3):
        response = cognito_user('1234', True)
        boto3.return_value.admin_get_user.return_value = response

        client = Client()
        user = client.get_user('1234')
        self.assertEqual(user, response)
        self.assertIn(
            call().admin_get_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_get_user_does_not_return_unmanaged(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', False)

        client = Client()
        user = client.get_user('1234')
        self.assertEqual(user, None)
        self.assertIn(
            call().admin_get_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_get_user_returns_unmanaged(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', False)

        client = Client()
        user = client.get_user('1234', return_unmanaged=True)
        self.assertEqual(user, cognito_user('1234', False))
        self.assertIn(
            call().admin_get_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_create_user_creates_managed(self, boto3):
        boto3.return_value.admin_get_user.return_value = None

        client = Client()
        created = client.create_user('1234', 'test@example.org')
        self.assertEqual(created, True)
        self.assertIn(
            call().admin_create_user(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }, {
                    'Name': 'custom:managed', 'Value': 'True'
                }],
                DesiredDeliveryMediums=['EMAIL']
            ),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_create_user_does_not_create_if_managed_exists(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', True)

        client = Client()
        created = client.create_user('1234', 'test@example.org')
        self.assertEqual(created, False)
        self.assertNotIn(
            call().admin_create_user(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }, {
                    'Name': 'custom:managed', 'Value': 'True'
                }],
                DesiredDeliveryMediums=['EMAIL']
            ),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_create_user_does_not_create_if_unmanaged_exists(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', False)

        client = Client()
        created = client.create_user('1234', 'test@example.org')
        self.assertEqual(created, False)
        self.assertNotIn(
            call().admin_create_user(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }, {
                    'Name': 'custom:managed', 'Value': 'True'
                }],
                DesiredDeliveryMediums=['EMAIL']
            ),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_delete_user_deletes_managed(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', True)

        client = Client()
        deleted = client.delete_user('1234')
        self.assertEqual(deleted, True)
        self.assertIn(
            call().admin_delete_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_delete_user_does_not_delete_unmanaged(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', False)

        client = Client()
        deleted = client.delete_user('1234')
        self.assertEqual(deleted, False)
        self.assertNotIn(
            call().admin_delete_user(UserPoolId=client.user_pool_id, Username='1234'),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_update_user_updates_managed(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', True)

        client = Client()
        updated = client.update_user('1234', 'test@example.org')
        self.assertEqual(updated, True)
        self.assertIn(
            call().admin_update_user_attributes(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }, {
                    'Name': 'custom:managed', 'Value': 'True'
                }]
            ),
            boto3.mock_calls
        )

    @patch('cognito.utils.client.client')
    def test_update_user_does_not_update_unmanaged(self, boto3):
        boto3.return_value.admin_get_user.return_value = cognito_user('1234', False)

        client = Client()
        updated = client.update_user('1234', 'test@example.org')
        self.assertEqual(updated, False)
        self.assertNotIn(
            call().admin_update_user_attributes(
                UserPoolId=client.user_pool_id,
                Username='1234',
                UserAttributes=[{
                    'Name': 'email', 'Value': 'test@example.org'
                }, {
                    'Name': 'custom:managed', 'Value': 'True'
                }]
            ),
            boto3.mock_calls
        )
