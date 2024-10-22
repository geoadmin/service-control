from io import StringIO
from unittest.mock import call
from unittest.mock import patch

from access.models import User
from provider.models import Provider

from django.core.management import call_command
from django.test import TestCase


def cognito_user(username, email):
    return {'Username': username, 'Attributes': [{'Name': 'email', 'Value': email}]}


class CognitoSyncCommandTest(TestCase):

    def setUp(self):
        self.provider = Provider.objects.create(
            acronym_de="BAFU",
            acronym_fr="OFEV",
            acronym_en="FOEN",
            acronym_it="UFAM",
            acronym_rm="UFAM",
            name_de="Bundesamt für Umwelt",
            name_fr="Office fédéral de l'environnement",
            name_en="Federal Office for the Environment",
            name_it="Ufficio federale dell'ambiente",
            name_rm="Uffizi federal per l'ambient",
        )

    def add_user(self, username, email):
        User.objects.create(
            username=username,
            first_name=username,
            last_name=username,
            email=email,
            provider=self.provider
        )

    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_adds(self, client):
        self.add_user('1', '1@example.org')
        client.return_value.list_users.return_value = []

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('adding user 1', out.getvalue())
        self.assertIn('1 user(s) added', out.getvalue())
        self.assertIn(call().create_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_deletes(self, client):
        client.return_value.list_users.return_value = [cognito_user('1', '1@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('deleting user 1', out.getvalue())
        self.assertIn('1 user(s) deleted', out.getvalue())
        self.assertIn(call().delete_user('1'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_updates(self, client):
        self.add_user('1', '1@example.org')
        client.return_value.list_users.return_value = [cognito_user('1', '2@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('updating user 1', out.getvalue())
        self.assertIn('1 user(s) updated', out.getvalue())
        self.assertIn(call().update_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_does_not_updates_if_unchanged(self, client):
        self.add_user('1', '1@example.org')
        client.return_value.list_users.return_value = [cognito_user('1', '1@example.org')]

        out = StringIO()
        call_command('cognito_sync', verbosity=2, stdout=out)

        self.assertIn('nothing to be done', out.getvalue())

    @patch('builtins.input')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_clears_if_confirmed(self, client, input_):
        input_.side_effect = ['yes']
        self.add_user('1', '1@example.org')
        client.return_value.list_users.side_effect = [[cognito_user('1', '1@example.org')], []]

        out = StringIO()
        call_command('cognito_sync', clear=True, verbosity=2, stdout=out)

        self.assertIn('this action will delete all managed users from cognito', out.getvalue())
        self.assertIn('deleting user 1', out.getvalue())
        self.assertIn('1 user(s) deleted', out.getvalue())
        self.assertIn('adding user 1', out.getvalue())
        self.assertIn('1 user(s) added', out.getvalue())
        self.assertIn(call().delete_user('1'), client.mock_calls)
        self.assertIn(call().create_user('1', '1@example.org'), client.mock_calls)

    @patch('builtins.input')
    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_does_not_clears_if_not_confirmed(self, client, input_):
        self.add_user('1', '1@example.org')
        input_.side_effect = ['no']
        client.return_value.list_users.side_effect = [[cognito_user('1', '1@example.org')], []]

        out = StringIO()
        call_command('cognito_sync', clear=True, verbosity=2, stdout=out)

        self.assertIn('this action will delete all managed users from cognito', out.getvalue())
        self.assertIn('operation cancelled', out.getvalue())
        self.assertNotIn(call().delete_user('1'), client.mock_calls)
        self.assertNotIn(call().create_user('1', '1@example.org'), client.mock_calls)

    @patch('cognito.management.commands.cognito_sync.Client')
    def test_command_runs_dry(self, client):
        self.add_user('1', '1@example.org')
        self.add_user('2', '2@example.org')
        client.return_value.list_users.return_value = [
            cognito_user('1', '10@example.org'), cognito_user('3', '3@example.org')
        ]

        out = StringIO()
        call_command('cognito_sync', dry_run=True, verbosity=2, stdout=out)

        self.assertIn('adding user 2', out.getvalue())
        self.assertIn('deleting user 3', out.getvalue())
        self.assertIn('updating user 1', out.getvalue())
        self.assertIn('dry run', out.getvalue())
        self.assertTrue(client().list_users.called)
        self.assertFalse(client().create_user.called)
        self.assertFalse(client().delete_user.called)
        self.assertFalse(client().update_user.called)
