import inspect
import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser


class CustomBaseCommand(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> None:
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError("subclasses of CustomBaseCommand must provide a handle() method")

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--logger', action='store_true', help='use logger configuration')


class CommandHandler():
    """Base class for management command handler

    This class add proper support for printing to the console for management command
    """

    def __init__(self, command: CustomBaseCommand, options: dict['str', Any]):
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        self.logger = logging.getLogger(mod.__name__ if mod else None)
        self.options = options
        self.verbosity = options['verbosity']
        self.use_logger = options.get('logger')
        self.stdout = command.stdout
        self.stderr = command.stderr
        self.style = command.style
        self.command = command

    def print(self, message: str, *args: Any, level: int = 2, **kwargs: Any) -> None:
        if self.verbosity >= level:
            if self.use_logger:
                self.logger.info(message, *args, **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(message % (args))

    def print_warning(self, message: str, *args: Any, level: int = 1, **kwargs: Any) -> None:
        if self.verbosity >= level:
            if self.use_logger:
                self.logger.warning(self.style.WARNING(message % (args)), **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(self.style.WARNING(message % (args)))

    def print_success(self, message: str, *args: Any, level: int = 1, **kwargs: Any) -> None:
        if self.verbosity >= level:
            if self.use_logger:
                self.logger.info(self.style.SUCCESS(message % (args)), **kwargs)
            else:
                if len(kwargs) > 0:
                    message = message + " " + ", ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                self.stdout.write(self.style.SUCCESS(message % (args)))

    def print_error(self, message: str, *args: Any, **kwargs: Any) -> None:
        if self.use_logger:
            self.logger.error(self.style.ERROR(message % (args)), **kwargs)
        else:
            if len(kwargs) > 0:
                message = message + "\n" + ", ".join(
                    f"{key}={value}" for key, value in kwargs.items()
                )
            self.stderr.write(self.style.ERROR(message % (args)))
