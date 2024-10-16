from unittest.mock import call
from unittest.mock import patch

from cognito.utils.user import create_user
from cognito.utils.user import disable_user
from cognito.utils.user import update_user

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

        created = create_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(created, True)
        self.assertIn(call.info('User %s created', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_create_user_does_not_create_existing_user(self, logger, client):
        client.return_value.create_user.return_value = False

        created = create_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(created, False)
        self.assertIn(call.warning('User %s already exists, not created', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_disable_user_disables_user(self, logger, client):
        client.return_value.disable_user.return_value = True

        disabled = disable_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(disabled, True)
        self.assertIn(call.info('User %s disabled', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_disable_user_does_not_disable_nonexisting_user(self, logger, client):
        client.return_value.disable_user.return_value = False

        disabled = disable_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(disabled, False)
        self.assertIn(
            call.warning('User %s does not exist, not disabled', '123'), logger.mock_calls
        )

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_user_updates_user(self, logger, client):
        client.return_value.update_user.return_value = True

        updated = update_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(updated, True)
        self.assertIn(call.info('User %s updated', '123'), logger.mock_calls)

    @patch('cognito.utils.user.Client')
    @patch('cognito.utils.user.logger')
    def test_update_user_does_not_update_nonexisting_user(self, logger, client):
        client.return_value.update_user.return_value = False

        updated = update_user(DummyUser('123', 'test@example.org'))

        self.assertEqual(updated, False)
        self.assertIn(call.warning('User %s does not exist, not updated', '123'), logger.mock_calls)
