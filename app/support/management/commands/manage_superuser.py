from typing import Any

import environ
from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.contrib.auth import get_user_model

env = environ.Env()


class Handler(CommandHandler):
    """Create or update superuser from information from the environment

    This command is used to make sure that the superuser is created and
    configured. The data for it will be created centrally in terraform.
    This will help with the password rotation.
    """

    def run(self) -> None:
        User = get_user_model()  # pylint: disable=invalid-name
        username = env.str('DJANGO_SUPERUSER_USERNAME')
        email = env.str('DJANGO_SUPERUSER_EMAIL')
        password = env.str('DJANGO_SUPERUSER_PASSWORD')

        try:
            admin = User.objects.get(username=username)
            operation = 'Updated'
        except User.DoesNotExist:
            admin = User.objects.create(username=username, email=email)
            operation = 'Created'

        admin.set_password(password)
        admin.save()
        self.print_success('%s the superuser %s', operation, username)


class Command(CustomBaseCommand):
    help = "Superuser management (creating or updating)"

    def handle(self, *args: Any, **options: Any) -> None:
        Handler(self, options).run()
