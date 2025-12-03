import sys
from logging import DEBUG
from logging import ERROR
from logging import FATAL
from logging import INFO
from unittest.mock import call
from unittest.mock import patch

from utils.logging import TimestampedStringIO
from utils.logging import redirect_std_to_logger


def test_timestamped_string_io():
    out = TimestampedStringIO(level=1)

    with patch('utils.logging.time', return_value=100):
        assert out.write('test') == 4
        assert out.messages == [(100, 1, 'test')]


def test_redirect_std_to_logger():
    with patch('utils.logging.getLogger') as logger:
        with redirect_std_to_logger('test'):
            sys.stdout.write('stdout 1')
            sys.stderr.write('stderr 1')
            sys.stderr.write('stderr 2\n')
            sys.stdout.write(' stdout 2')

    assert logger.mock_calls == [
        call('test'),
        call().log(INFO, 'stdout 1'),
        call().log(ERROR, 'stderr 1'),
        call().log(ERROR, 'stderr 2'),
        call().log(INFO, 'stdout 2'),
    ]


def test_redirect_std_to_logger_custom_level():
    with patch('utils.logging.getLogger') as logger:
        with redirect_std_to_logger('test', stderr_level=FATAL, stdout_level=DEBUG):
            sys.stdout.write('stdout 1')
            sys.stderr.write('stderr 1')
            sys.stderr.write('stderr 2\n')
            sys.stdout.write(' stdout 2')

    assert logger.mock_calls == [
        call('test'),
        call().log(DEBUG, 'stdout 1'),
        call().log(FATAL, 'stderr 1'),
        call().log(FATAL, 'stderr 2'),
        call().log(DEBUG, 'stdout 2'),
    ]


def test_redirect_std_to_logger_exception():
    exception = RuntimeError('abort')
    with patch('utils.logging.getLogger') as logger:
        with redirect_std_to_logger('test'):
            sys.stdout.write('stdout 1')
            sys.stderr.write(' stderr 1\n')
            raise exception

    assert logger.mock_calls == [
        call('test'),
        call().log(INFO, 'stdout 1'),
        call().log(ERROR, 'stderr 1'),
        call().exception(exception),
    ]
