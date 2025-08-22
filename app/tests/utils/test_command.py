from io import StringIO
from unittest.mock import MagicMock
from unittest.mock import call

from utils.command import CommandHandler
from utils.command import CustomBaseCommand

from django.core.management import call_command


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


def test_print_to_stdout_default_verbosity():
    # default verbosity == 1
    out = StringIO()
    err = StringIO()
    call_command(Command(), stdout=out, stderr=err)
    assert "Print default" not in out.getvalue()
    assert "Print 0" in out.getvalue()
    assert "Print 1" in out.getvalue()
    assert "Print 2" not in out.getvalue()
    assert "Success default" in out.getvalue()
    assert "Success 0" in out.getvalue()
    assert "Success 1" in out.getvalue()
    assert "Success 2" not in out.getvalue()
    assert "Warning default" in out.getvalue()
    assert "Warning 0" in out.getvalue()
    assert "Warning 1" in out.getvalue()
    assert "Warning 2" not in out.getvalue()
    assert "Error" in err.getvalue()


def test_print_to_stdout_verbosity_0():
    out = StringIO()
    err = StringIO()
    call_command(Command(), verbosity=0, stdout=out, stderr=err)
    assert "Print 0" in out.getvalue()
    assert "Print 1" not in out.getvalue()
    assert "Print 2" not in out.getvalue()
    assert "Success 0" in out.getvalue()
    assert "Success 1" not in out.getvalue()
    assert "Success 2" not in out.getvalue()
    assert "Warning 0" in out.getvalue()
    assert "Warning 1" not in out.getvalue()
    assert "Warning 2" not in out.getvalue()
    assert "Error" in err.getvalue()


def test_print_to_stdout_verbosity_3():
    out = StringIO()
    err = StringIO()
    call_command(Command(), verbosity=3, stdout=out, stderr=err)
    assert "Print 0" in out.getvalue()
    assert "Print 1" in out.getvalue()
    assert "Print 2" in out.getvalue()
    assert "Success 0" in out.getvalue()
    assert "Success 1" in out.getvalue()
    assert "Success 2" in out.getvalue()
    assert "Warning 0" in out.getvalue()
    assert "Warning 1" in out.getvalue()
    assert "Warning 2" in out.getvalue()
    assert "Error" in err.getvalue()


def test_print_to_stdout_args_kwargs():
    out = StringIO()
    err = StringIO()
    call_command(Command(), verbosity=3, stdout=out, stderr=err)
    assert "Print JohnDoe" in out.getvalue()
    assert "Print extra={'n': 'JohnDoe'}" in out.getvalue()
    assert "Print John extra={'n': 'Doe'}" in out.getvalue()
    assert "Success JohnDoe" in out.getvalue()
    assert "Success extra={'n': 'JohnDoe'}" in out.getvalue()
    assert "Success John extra={'n': 'Doe'}" in out.getvalue()
    assert "Warning JohnDoe" in out.getvalue()
    assert "Warning extra={'n': 'JohnDoe'}" in out.getvalue()
    assert "Warning John extra={'n': 'Doe'}" in out.getvalue()
    assert "Error JohnDoe" in err.getvalue()
    assert "Error\nextra={'n': 'JohnDoe'}" in err.getvalue()
    assert "Error John\nextra={'n': 'Doe'}" in err.getvalue()


def test_print_to_log_default_verbosity():
    # default verbosity == 1
    command = Command()
    call_command(command, logger=True)
    calls = command.handler.logger.mock_calls
    assert call.info("Print default") not in calls
    assert call.info("Print 0") in calls
    assert call.info("Print 1") in calls
    assert call.info("Print 2") not in calls
    assert call.info("Success default") in calls
    assert call.info("Success 0") in calls
    assert call.info("Success 1") in calls
    assert call.info("Success 2") not in calls
    assert call.warning("Warning default") in calls
    assert call.warning("Warning 0") in calls
    assert call.warning("Warning 1") in calls
    assert call.warning("Warning 2") not in calls
    assert call.error("Error") in calls


def test_print_to_log_verbosity_0():
    command = Command()
    call_command(command, verbosity=0, logger=True)
    calls = command.handler.logger.mock_calls
    assert call.info("Print 0") in calls
    assert call.info("Print 1") not in calls
    assert call.info("Print 2") not in calls
    assert call.info("Success 0") in calls
    assert call.info("Success 1") not in calls
    assert call.info("Success 2") not in calls
    assert call.warning("Warning 0") in calls
    assert call.warning("Warning 1") not in calls
    assert call.warning("Warning 2") not in calls
    assert call.error("Error") in calls


def test_print_to_log_verbosity_3():
    command = Command()
    call_command(command, verbosity=3, logger=True)
    calls = command.handler.logger.mock_calls
    assert call.info("Print 0") in calls
    assert call.info("Print 1") in calls
    assert call.info("Print 2") in calls
    assert call.info("Success 0") in calls
    assert call.info("Success 1") in calls
    assert call.info("Success 2") in calls
    assert call.warning("Warning 0") in calls
    assert call.warning("Warning 1") in calls
    assert call.warning("Warning 2") in calls
    assert call.error("Error") in calls


def test_print_to_log_args_kwargs():
    command = Command()
    call_command(command, verbosity=3, logger=True)
    calls = command.handler.logger.mock_calls
    assert call.info("Print %s", "JohnDoe") in calls
    assert call.info("Print", extra={"n": "JohnDoe"}) in calls
    assert call.info("Print %s", "John", extra={"n": "Doe"}) in calls
    assert call.info("Success JohnDoe") in calls
    assert call.info("Success", extra={"n": "JohnDoe"}) in calls
    assert call.info("Success John", extra={"n": "Doe"}) in calls
    assert call.warning("Warning JohnDoe") in calls
    assert call.warning("Warning", extra={"n": "JohnDoe"}) in calls
    assert call.warning("Warning John", extra={"n": "Doe"}) in calls
    assert call.error("Error JohnDoe") in calls
    assert call.error("Error", extra={"n": "JohnDoe"}) in calls
    assert call.error("Error John", extra={"n": "Doe"}) in calls
