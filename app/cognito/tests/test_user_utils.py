from unittest.mock import call
from unittest.mock import patch

from cognito.utils.user import create_cognito_user
from cognito.utils.user import delete_cognito_user
from cognito.utils.user import update_cognito_user

from django.test import TestCase


class DummyUser:

    def __init__(self, username, email):
        self.username = username
        self.email = email


class ClientTestCase(TestCase):

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_create_user_creates_user(self, logger, client):
        client.return_value.create_user.return_value = True

        created = create_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(created, True)
        self.assertIn(call.info('User %s created', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_create_user_does_not_create_existing_user(self, logger, client):
        client.return_value.create_user.return_value = False

        created = create_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(created, False)
        self.assertIn(
            call.critical('User %s already exists, not created', '123'), logger.mock_calls
        )

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_delete_user_deletes_user(self, logger, client):
        client.return_value.delete_user.return_value = True

        deleted = delete_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(deleted, True)
        self.assertIn(call.info('User %s deleted', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_delete_user_does_not_delete_nonexisting_user(self, logger, client):
        client.return_value.delete_user.return_value = False

        deleted = delete_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(deleted, False)
        self.assertIn(
            call.critical('User %s does not exist, not deleted', '123'), logger.mock_calls
        )

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_cognito_user_updates_user(self, logger, client):
        client.return_value.update_user.return_value = True

        updated = update_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(updated, True)
        self.assertIn(call.info('User %s updated', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_cognito_user_does_not_update_nonexisting_user(self, logger, client):
        client.return_value.update_user.return_value = False

        updated = update_cognito_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(updated, False)
        self.assertIn(call.warning('User %s does not exist, not updated', '123'), logger.mock_calls)
