from io import StringIO
from unittest.mock import call
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class DummyUser:

    def __init__(self, id_, email):
        self.id = id_
        self.email = email


def cognito_user(username, email):
    return {'Username': username, 'Attributes': [{'Name': 'email', 'Value': email}]}


class CognitoSyncCommandTest(TestCase):

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_adds(self, client, users):
        users.return_value = [DummyUser(1, '1@example.org')]
        client.return_value.get_users.return_value = []

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('adding user 1', out.getvalue())
        self.assertIn('1 user(s) added', out.getvalue())
        self.assertIn(call().create_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_removes(self, client, users):
        users.return_value = []
        client.return_value.get_users.return_value = [cognito_user('1', '1@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('deleting user 1', out.getvalue())
        self.assertIn('1 user(s) deleted', out.getvalue())
        self.assertIn(call().delete_user('1'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_updates(self, client, users):
        users.return_value = [DummyUser(1, '1@example.org')]
        client.return_value.get_users.return_value = [cognito_user('1', '2@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('updating user 1', out.getvalue())
        self.assertIn('1 user(s) updated', out.getvalue())
        self.assertIn(call().update_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_does_not_updates_if_unchanged(self, client, users):
        users.return_value = [DummyUser(1, '1@example.org')]
        client.return_value.get_users.return_value = [cognito_user('1', '1@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('nothing to be done', out.getvalue())

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_clears(self, client, users):
        users.return_value = [DummyUser(1, '1@example.org')]
        client.return_value.get_users.side_effect = [[cognito_user('1', '1@example.org')], []]

        out = StringIO()
        call_command('cognito_sync', clear=True, verbosity=2, stdout=out)

        self.assertIn('deleting user 1', out.getvalue())
        self.assertIn('1 user(s) deleted', out.getvalue())
        self.assertIn('adding user 1', out.getvalue())
        self.assertIn('1 user(s) added', out.getvalue())
        self.assertIn(call().delete_user('1'), client.mock_calls)
        self.assertIn(call().create_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.get_local_users')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_runs_dry(self, client, users):
        users.return_value = [DummyUser(1, '1@example.org'), DummyUser(2, '2@example.org')]
        client.return_value.get_users.return_value = [
            cognito_user('1', '10@example.org'), cognito_user('3', '3@example.org')
        ]

        out = StringIO()
        call_command('cognito_sync', dry_run=True, verbosity=2, stdout=out)

        self.assertIn('adding user 2', out.getvalue())
        self.assertIn('deleting user 3', out.getvalue())
        self.assertIn('updating user 1', out.getvalue())
        self.assertIn('dry run', out.getvalue())
        self.assertEqual([call(), call().get_users()], client.mock_calls)
