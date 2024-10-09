from io import StringIO
from unittest.mock import MagicMock
from unittest.mock import call

from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management import call_command
from django.test import TestCase


class Handler(CommandHandler):

    def __init__(self, command, options):
        super().__init__(command, options)
        self.logger = MagicMock()

    def run(self):
        # level
        self.print("Print default")
        self.print("Print 0", level=0)
        self.print("Print 1", level=1)
        self.print("Print 2", level=2)
        self.print_success("Success default")
        self.print_success("Success 0", level=0)
        self.print_success("Success 1", level=1)
        self.print_success("Success 2", level=2)
        self.print_warning("Warning default")
        self.print_warning("Warning 0", level=0)
        self.print_warning("Warning 1", level=1)
        self.print_warning("Warning 2", level=2)
        self.print_error("Error")

        # args and kwargs
        self.print("Print %s", "JohnDoe")
        self.print("Print", extra={"n": "JohnDoe"})
        self.print("Print %s", "John", extra={"n": "Doe"})
        self.print_success("Success %s", "JohnDoe")
        self.print_success("Success", extra={"n": "JohnDoe"})
        self.print_success("Success %s", "John", extra={"n": "Doe"})
        self.print_warning("Warning %s", "JohnDoe")
        self.print_warning("Warning", extra={"n": "JohnDoe"})
        self.print_warning("Warning %s", "John", extra={"n": "Doe"})
        self.print_error("Error %s", "JohnDoe")
        self.print_error("Error", extra={"n": "JohnDoe"})
        self.print_error("Error %s", "John", extra={"n": "Doe"})


class Command(CustomBaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = None

    def handle(self, *args, **options):
        self.handler = Handler(self, options)
        self.handler.run()


class CustomCommandTest(TestCase):

    def test_print_to_stdout_default_verbosity(self):
        # no verbosity given = 1
        out = StringIO()
        err = StringIO()
        call_command(Command(), stdout=out, stderr=err)
        self.assertNotIn("Print default", out.getvalue())
        self.assertIn("Print 0", out.getvalue())
        self.assertIn("Print 1", out.getvalue())
        self.assertNotIn("Print 2", out.getvalue())
        self.assertIn("Success default", out.getvalue())
        self.assertIn("Success 0", out.getvalue())
        self.assertIn("Success 1", out.getvalue())
        self.assertNotIn("Success 2", out.getvalue())
        self.assertIn("Warning default", out.getvalue())
        self.assertIn("Warning 0", out.getvalue())
        self.assertIn("Warning 1", out.getvalue())
        self.assertNotIn("Warning 2", out.getvalue())
        self.assertIn("Error", err.getvalue())

    def test_print_to_stdout_verbosity_0(self):
        out = StringIO()
        err = StringIO()
        call_command(Command(), verbosity=0, stdout=out, stderr=err)
        self.assertIn("Print 0", out.getvalue())
        self.assertNotIn("Print 1", out.getvalue())
        self.assertNotIn("Print 2", out.getvalue())
        self.assertIn("Success 0", out.getvalue())
        self.assertNotIn("Success 1", out.getvalue())
        self.assertNotIn("Success 2", out.getvalue())
        self.assertIn("Warning 0", out.getvalue())
        self.assertNotIn("Warning 1", out.getvalue())
        self.assertNotIn("Warning 2", out.getvalue())
        self.assertIn("Error", err.getvalue())

    def test_print_to_stdout_verbosity_3(self):
        out = StringIO()
        err = StringIO()
        call_command(Command(), verbosity=3, stdout=out, stderr=err)
        self.assertIn("Print 0", out.getvalue())
        self.assertIn("Print 1", out.getvalue())
        self.assertIn("Print 2", out.getvalue())
        self.assertIn("Success 0", out.getvalue())
        self.assertIn("Success 1", out.getvalue())
        self.assertIn("Success 2", out.getvalue())
        self.assertIn("Warning 0", out.getvalue())
        self.assertIn("Warning 1", out.getvalue())
        self.assertIn("Warning 2", out.getvalue())
        self.assertIn("Error", err.getvalue())

    def test_print_to_stdout_args_kwargs(self):
        out = StringIO()
        err = StringIO()
        call_command(Command(), verbosity=3, stdout=out, stderr=err)
        self.assertIn("Print JohnDoe", out.getvalue())
        self.assertIn("Print extra={'n': 'JohnDoe'}", out.getvalue())
        self.assertIn("Print John extra={'n': 'Doe'}", out.getvalue())
        self.assertIn("Success JohnDoe", out.getvalue())
        self.assertIn("Success extra={'n': 'JohnDoe'}", out.getvalue())
        self.assertIn("Success John extra={'n': 'Doe'}", out.getvalue())
        self.assertIn("Warning JohnDoe", out.getvalue())
        self.assertIn("Warning extra={'n': 'JohnDoe'}", out.getvalue())
        self.assertIn("Warning John extra={'n': 'Doe'}", out.getvalue())
        self.assertIn("Error JohnDoe", err.getvalue())
        self.assertIn("Error\nextra={'n': 'JohnDoe'}", err.getvalue())
        self.assertIn("Error John\nextra={'n': 'Doe'}", err.getvalue())

    def test_print_to_log_default_verbosity(self):
        # no verbosity given = 1
        command = Command()
        call_command(command, logger=True)
        calls = command.handler.logger.mock_calls
        self.assertNotIn(call.info("Print default"), calls)
        self.assertIn(call.info("Print 0"), calls)
        self.assertIn(call.info("Print 1"), calls)
        self.assertNotIn(call.info("Print 2"), calls)
        self.assertIn(call.info("Success default"), calls)
        self.assertIn(call.info("Success 0"), calls)
        self.assertIn(call.info("Success 1"), calls)
        self.assertNotIn(call.info("Success 2"), calls)
        self.assertIn(call.warning("Warning default"), calls)
        self.assertIn(call.warning("Warning 0"), calls)
        self.assertIn(call.warning("Warning 1"), calls)
        self.assertNotIn(call.warning("Warning 2"), calls)
        self.assertIn(call.error("Error"), calls)

    def test_print_to_log_verbosity_0(self):
        command = Command()
        call_command(command, verbosity=0, logger=True)
        calls = command.handler.logger.mock_calls
        self.assertIn(call.info("Print 0"), calls)
        self.assertNotIn(call.info("Print 1"), calls)
        self.assertNotIn(call.info("Print 2"), calls)
        self.assertIn(call.info("Success 0"), calls)
        self.assertNotIn(call.info("Success 1"), calls)
        self.assertNotIn(call.info("Success 2"), calls)
        self.assertIn(call.warning("Warning 0"), calls)
        self.assertNotIn(call.warning("Warning 1"), calls)
        self.assertNotIn(call.warning("Warning 2"), calls)
        self.assertIn(call.error("Error"), calls)

    def test_print_to_log_verbosity_3(self):
        command = Command()
        call_command(command, verbosity=3, logger=True)
        calls = command.handler.logger.mock_calls
        self.assertIn(call.info("Print 0"), calls)
        self.assertIn(call.info("Print 1"), calls)
        self.assertIn(call.info("Print 2"), calls)
        self.assertIn(call.info("Success 0"), calls)
        self.assertIn(call.info("Success 1"), calls)
        self.assertIn(call.info("Success 2"), calls)
        self.assertIn(call.warning("Warning 0"), calls)
        self.assertIn(call.warning("Warning 1"), calls)
        self.assertIn(call.warning("Warning 2"), calls)
        self.assertIn(call.error("Error"), calls)

    def test_print_to_log_args_kwargs(self):
        command = Command()
        call_command(command, verbosity=3, logger=True)
        calls = command.handler.logger.mock_calls
        self.assertIn(call.info('Print %s', 'JohnDoe'), calls)
        self.assertIn(call.info('Print', extra={'n': 'JohnDoe'}), calls)
        self.assertIn(call.info('Print %s', 'John', extra={'n': 'Doe'}), calls)
        self.assertIn(call.info('Success JohnDoe'), calls)
        self.assertIn(call.info('Success', extra={'n': 'JohnDoe'}), calls)
        self.assertIn(call.info('Success John', extra={'n': 'Doe'}), calls)
        self.assertIn(call.warning('Warning JohnDoe'), calls)
        self.assertIn(call.warning('Warning', extra={'n': 'JohnDoe'}), calls)
        self.assertIn(call.warning('Warning John', extra={'n': 'Doe'}), calls)
        self.assertIn(call.error('Error JohnDoe'), calls)
        self.assertIn(call.error('Error', extra={'n': 'JohnDoe'}), calls)
        self.assertIn(call.error('Error John', extra={'n': 'Doe'}), calls)
