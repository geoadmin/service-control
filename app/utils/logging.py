from contextlib import contextmanager
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
from logging import ERROR
from logging import INFO
from logging import getLogger
from logging.config import dictConfig
from time import time
from typing import Generator

from django.conf import settings


class TimestampedStringIO(StringIO):

    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level
        self.messages: list[tuple[float, int, str]] = []

    def write(self, s: str) -> int:
        self.messages.append((time(), self.level, s))
        return len(s)


@contextmanager
def redirect_std_to_logger(name: str,
                           stderr_level: int = ERROR,
                           stdout_level: int = INFO) -> Generator[None, None, None]:
    stderr = TimestampedStringIO(stderr_level)
    stdout = TimestampedStringIO(stdout_level)
    exception: Exception | None = None
    with redirect_stderr(stderr), redirect_stdout(stdout):
        try:
            yield
        except Exception as e:  # pylint: disable=broad-exception-caught
            exception = e

    logger = getLogger(name)
    dictConfig(settings.LOGGING)
    for _, level, message in sorted(stderr.messages + stdout.messages):
        logger.log(level, message)
    if exception:
        logger.exception(exception)
