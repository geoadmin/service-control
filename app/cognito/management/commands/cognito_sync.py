from typing import Any

from cognito.utils.client import Client
from cognito.utils.user import User
from mypy_boto3_cognito_idp.type_defs import UserTypeTypeDef
from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management.base import CommandParser


def get_local_users() -> list[User]:
    # TODO: remove me!
    return []


class Handler(CommandHandler):

    def __init__(self, command: CustomBaseCommand, options: dict[str, Any]) -> None:
        super().__init__(command, options)
        self.clear = options['clear']
        self.dry_run = options['dry_run']
        self.client = Client()
        self.counts = {'added': 0, 'deleted': 0, 'updated': 0}

    def attributes_to_dict(self, user: UserTypeTypeDef) -> dict[str, str]:
        """ Converts the attributes from a cognito uses to a dict. """
        return {attribute['Name']: attribute['Value'] for attribute in user.get('Attributes', {})}

    def clear_users(self) -> None:
        """ Remove all existing cognito users. """

        for user in self.client.get_users():
            self.counts['deleted'] += 1
            username = user['Username']
            self.print(f'deleting user {username}')
            if not self.dry_run:
                self.client.delete_user(username)

    def sync_users(self) -> None:
        """ Synchronizes local and cognito users. """

        # Get all remote and local users
        local = {str(user.id): user for user in get_local_users()}
        remote = {user['Username']: user for user in self.client.get_users()}

        # Add local only user
        for username in set(local.keys()).difference(set(remote.keys())):
            self.counts['added'] += 1
            self.print(f'adding user {username}')
            if not self.dry_run:
                self.client.create_user(username, local[username].email)

        # Remove remote only user
        for username in set(remote.keys()).difference(set(local.keys())):
            self.counts['deleted'] += 1
            self.print(f'deleting user {username}')
            if not self.dry_run:
                self.client.delete_user(username)

        # Update common users
        for username in set(local.keys()).intersection(set(remote.keys())):
            if local[username].email != self.attributes_to_dict(remote[username]).get('email'):
                self.counts['updated'] += 1
                self.print(f'updating user {username}')
                if not self.dry_run:
                    self.client.update_user(username, local[username].email)

    def run(self) -> None:
        """ Main entry point of command. """

        # Clear data
        if self.clear:
            self.clear_users()

        # Sync data
        self.sync_users()

        # Print counts
        printed = False
        for operation, count in self.counts.items():
            if count:
                printed = True
                self.print_success(f'{count} user(s) {operation}')
        if not printed:
            self.print_success('nothing to be done')

        if self.dry_run:
            self.print_warning('dry run, nothing has been done')


class Command(CustomBaseCommand):
    help = "Synchronizes local users with cognito"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing users in cognito before synchronizing',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run, abort transaction in the end',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        Handler(self, options).run()
