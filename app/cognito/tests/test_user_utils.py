from unittest.mock import call
from unittest.mock import patch

from cognito.utils.user import add_user
from cognito.utils.user import delete_user
from cognito.utils.user import update_user

from django.test import TestCase


class DummyUser:

    def __init__(self, id_, email):
        self.id = id_
        self.email = email


class ClientTestCase(TestCase):

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_add_user_adds_user(self, logger, client):
        client.return_value.get_user.return_value = None

        add_user(DummyUser(123, 'test@example.org'))

        self.assertIn(call().create_user('123', 'test@example.org'), client.mock_calls)
        self.assertIn(call.info('User %s created', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_add_user_updates_existing_user(self, logger, client):
        client.return_value.get_user.return_value = {'Username': '123'}

        add_user(DummyUser(123, 'test@example.org'))

        self.assertIn(call().update_user('123', 'test@example.org'), client.mock_calls)
        self.assertIn(call.info('User %s created', '123'), logger.mock_calls)
        self.assertIn(call.warning('User %s already exists, updating', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_delete_user_deletes_user(self, logger, client):
        client.return_value.get_user.return_value = {'Username': '123'}

        delete_user(DummyUser(123, 'test@example.org'))

        self.assertIn(call().delete_user('123'), client.mock_calls)
        self.assertIn(call.info('User %s deleted', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_delete_when_user_not_exists(self, logger, client):
        client.return_value.get_user.return_value = None

        delete_user(DummyUser(123, 'test@example.org'))

        self.assertIn(call.info('User %s deleted', '123'), logger.mock_calls)
        self.assertIn(call.warning('User %s does not exist, ignoring', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_user_updates_user(self, logger, client):
        client.return_value.get_user.return_value = {'Username': '123'}

        update_user(DummyUser(123, 'test@example.org'))

        self.assertIn(call().update_user('123', 'test@example.org'), client.mock_calls)
        self.assertIn(call.info('User %s updated', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_user_adds_non_existing_user(self, logger, client):
        client.return_value.get_user.return_value = None

        update_user(DummyUser(123, 'test@example.org'))

        self.assertNotIn(call().add_user('123', 'test@example.org'), client.mock_calls)
        self.assertIn(call.info('User %s updated', '123'), logger.mock_calls)
        self.assertIn(call.warning('User %s does not exist, adding', '123'), logger.mock_calls)
