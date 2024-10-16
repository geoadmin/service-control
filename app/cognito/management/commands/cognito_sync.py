from typing import Any

from cognito.utils.client import Client
from cognito.utils.client import user_attributes_to_dict
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

    def clear_users(self) -> None:
        """ Remove all existing cognito users. """

        for user in self.client.list_users():
            self.counts['deleted'] += 1
            username = user['Username']
            self.print(f'deleting user {username}')
            if not self.dry_run:
                deleted = self.client.delete_user(username)
                if not deleted:
                    self.print_error('Could not delete %s', username)

    def add_user(self, user: User) -> None:
        """ Add a local user to cognito. """

        self.counts['added'] += 1
        self.print(f'adding user {user.username}')
        if not self.dry_run:
            created = self.client.create_user(user.username, user.email)
            if not created:
                self.print_error('Could not create %s', user.username)

    def delete_user(self, username: str) -> None:
        """ Delete a remote user from cognito. """

        self.counts['deleted'] += 1
        self.print(f'deleting user {username}')
        if not self.dry_run:
            deleted = self.client.delete_user(username)
            if not deleted:
                self.print_error('Could not delete %s', username)

    def update_user(self, local_user: User, remote_user: UserTypeTypeDef) -> None:
        """ Update a remote user in cognito. """

        remote_attributes = user_attributes_to_dict(remote_user['Attributes'])
        if local_user.email != remote_attributes.get('email'):
            self.counts['updated'] += 1
            self.print(f'updating user {local_user.username}')
            if not self.dry_run:
                updated = self.client.update_user(local_user.username, local_user.email)
                if not updated:
                    self.print_error('Could not update %s', local_user.username)

    def sync_users(self) -> None:
        """ Synchronizes local and cognito users. """

        # Get all remote and local users
        local_users = {user.username: user for user in get_local_users()}
        local_usernames = set(local_users.keys())
        remote_users = {user['Username']: user for user in self.client.list_users()}
        remote_usernames = set(remote_users.keys())

        for username in local_usernames.difference(remote_usernames):
            self.add_user(local_users[username])

        for username in remote_usernames.difference(local_usernames):
            self.delete_user(username)

        for username in local_usernames.intersection(remote_usernames):
            self.update_user(local_users[username], remote_users[username])

    def run(self) -> None:
        """ Main entry point of command. """

        # Clear data
        if self.clear:
            self.print_warning('this action will delete all managed users from cognito', level=0)
            confirm = input('are you sure you want to proceed? [yes/no]: ')
            if confirm.lower() != 'yes':
                self.print_warning('operation cancelled', level=0)
                return

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
