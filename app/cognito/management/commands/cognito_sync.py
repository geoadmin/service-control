from typing import TYPE_CHECKING
from typing import Any
from typing import TextIO

from access.models import User
from cognito.utils.client import Client
from cognito.utils.client import user_attributes_to_dict
from utils.command import CustomBaseCommand

from django.core.management.base import CommandParser

if TYPE_CHECKING:
    from mypy_boto3_cognito_idp.type_defs import UserTypeTypeDef


class Command(CustomBaseCommand):
    help = "Synchronizes local users with cognito"

    def __init__(
        self,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
        no_color: bool = False,
        force_color: bool = False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.client = Client()
        self.counts = {'added': 0, 'deleted': 0, 'updated': 0, 'enabled': 0, 'disabled': 0}

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

    def clear_users(self) -> None:
        """ Remove all existing cognito users. """

        for user in self.client.list_users():
            self.counts['deleted'] += 1
            user_id = user['Username']
            self.print(f'deleting user {user_id}')
            if not self.options['dry_run']:
                deleted = self.client.delete_user(user_id)
                if not deleted:
                    self.print_error(
                        'Could not delete %s, might not exist or might be unmanged', user_id
                    )

    def add_user(self, user: User) -> None:
        """ Add a local user to cognito. """

        self.counts['added'] += 1
        self.print(f'adding user {user.user_id}')
        if not self.options['dry_run']:
            created = self.client.create_user(user.user_id, user.username, user.email)
            if not created:
                self.print_error(
                    'Could not create %s, might already exist as unmanaged user', user.user_id
                )

    def delete_user(self, user_id: str) -> None:
        """ Delete a remote user from cognito. """

        self.counts['deleted'] += 1
        self.print(f'deleting user {user_id}')
        if not self.options['dry_run']:
            deleted = self.client.delete_user(user_id)
            if not deleted:
                self.print_error(
                    'Could not delete %s, might not exist or might be unmanaged', user_id
                )

    def update_user(self, local_user: User, remote_user: 'UserTypeTypeDef') -> None:
        """ Update a remote user in cognito. """

        remote_attributes = user_attributes_to_dict(remote_user['Attributes'])
        changed = (
            local_user.email != remote_attributes.get('email') or
            local_user.username != remote_attributes.get('preferred_username')
        )
        if changed:
            self.counts['updated'] += 1
            self.print(f'updating user {local_user.user_id}')
            if not self.options['dry_run']:
                updated = self.client.update_user(
                    local_user.user_id, local_user.username, local_user.email
                )
                if not updated:
                    self.print_error(
                        'Could not update %s, might not exist or might be unmanaged',
                        local_user.user_id
                    )

        if local_user.is_active != remote_user['Enabled']:
            if local_user.is_active:
                self.counts['enabled'] += 1
                self.print(f'enabling user {local_user.user_id}')
                if not self.options['dry_run']:
                    enabled = self.client.enable_user(local_user.user_id)
                    if not enabled:
                        self.print_error('Could not enable %s', local_user.user_id)
            else:
                self.counts['disabled'] += 1
                self.print(f'disabling user {local_user.user_id}')
                if not self.options['dry_run']:
                    disabled = self.client.disable_user(local_user.user_id)
                    if not disabled:
                        self.print_error('Could not disable %s', local_user.user_id)

    def sync_users(self) -> None:
        """ Synchronizes local and cognito users. """

        # Get all remote and local users
        local_users = {user.user_id: user for user in User.all_objects.all()}
        local_user_ids = set(local_users.keys())
        remote_users = {user['Username']: user for user in self.client.list_users()}
        remote_user_ids = set(remote_users.keys())

        for user_id in local_user_ids.difference(remote_user_ids):
            self.add_user(local_users[user_id])

        for user_id in remote_user_ids.difference(local_user_ids):
            self.delete_user(user_id)

        for user_id in local_user_ids.intersection(remote_user_ids):
            self.update_user(local_users[user_id], remote_users[user_id])

    def handle(self, *args: Any, **options: Any) -> None:
        """ Main entry point of command. """

        # Clear data
        if self.options['clear']:
            self.print_warning('This action will delete all managed users from cognito', level=0)
            confirm = input('are you sure you want to proceed? [yes/no]: ')
            if confirm.lower() != 'yes':
                self.print_warning('operation cancelled', level=0)
                return

            self.clear_users()

        self.sync_users()

        # Print counts
        printed = False
        for operation, count in self.counts.items():
            if count:
                printed = True
                self.print_success(f'{count} user(s) {operation}')
        if not printed:
            self.print_success('nothing to be done')

        if self.options['dry_run']:
            self.print_warning('dry run, nothing has been done')
