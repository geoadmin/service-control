import logging
from typing import Any
from typing import TextIO

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser


# This class is also used in service-stac. Ensure that any changes made here are reflected there
# as well.
class CustomBaseCommand(BaseCommand):
    """
    A custom Django management command that adds proper support for logging.

    Example how to subclass:

        class MyCommand(CustomBaseCommand):

            def add_arguments(self, parser: CommandParser) -> None:
                super().add_arguments(parser)
                parser.add_argument('--flag', action='store_true')

            def handle(self, *args: Any, **options: dict['str', Any]) -> None:
                if options['flag']:  # or self.options['flag']
                    self.print('flag was set')
                self.print_success('done')

    """

    def __init__(
        self,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
        no_color: bool = False,
        force_color: bool = False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.logger = logging.getLogger(self.__module__)
        self.options: dict['str', Any] = {}

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Entry point for add custom arguments. Options will also be available as self.options during
        handle.

        Subclasses may want to extend this method.
        """

        parser.add_argument('--logger', action='store_true', help='use logger configuration')

    def handle(self, *args: Any, **options: dict['str', Any]) -> None:
        """
        The actual logic of the command.

        Subclasses must implement this method.
        """

        raise NotImplementedError("subclasses of CustomBaseCommand must provide a handle() method")

    def execute(self, *args: Any, **options: dict['str', Any]) -> None:
        """ Try to execute the command and log any exceptions if the logger is configured. """

        self.options = options
        if self.options['logger']:
            try:
                super().execute(*args, **options)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.print_error(e, exc_info=True)
        else:
            super().execute(*args, **options)

    def print(self, message: str, *args: Any, level: int = 2, **kwargs: Any) -> None:
        if self.options['verbosity'] >= level:
            if self.options['logger']:
                self.logger.info(message, *args, **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(message % (args))

    def print_warning(self, message: str, *args: Any, level: int = 1, **kwargs: Any) -> None:
        if self.options['verbosity'] >= level:
            if self.options['logger']:
                self.logger.warning(message, *args, **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(self.style.WARNING(message % (args)))

    def print_success(self, message: str, *args: Any, level: int = 1, **kwargs: Any) -> None:
        if self.options['verbosity'] >= level:
            if self.options['logger']:
                self.logger.info(message, *args, **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(self.style.SUCCESS(message % (args)))

    def print_error(self, message: str | Exception, *args: Any, **kwargs: Any) -> None:
        if self.options['logger']:
            self.logger.error(message, *args, **kwargs)
        else:
            message = str(message)
            if len(kwargs) > 0:
                message = message + "\n" + ", ".join(
                    f"{key}={value}" for key, value in kwargs.items()
                )
            self.stderr.write(self.style.ERROR(message % (args)))
