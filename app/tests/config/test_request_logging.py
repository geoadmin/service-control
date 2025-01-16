# Testing that the logging calls correctly pass their arguments
# The logging is sent to the ecs formatter, which converts them
# to JSON objects. These are to be consumed by the ECS pipelines
# and displayed in kibana

import json

import mock_api  # pylint: disable=unused-import
import pytest
from ecs_logging import StdlibFormatter


@pytest.fixture(name='configure_logger')
def fixture_configure_logger(caplog):
    caplog.handler.setFormatter(StdlibFormatter())


def test_404_logging(client, caplog, configure_logger):
    path = '/api/v1/trigger-not-found'
    client.get(path)

    log_entry = json.loads(caplog.text)

    assert log_entry['log.level'] == 'warning'
    assert log_entry['message'] == f'Response 404 on {path}'
    assert log_entry['http']['request']['method'] == 'GET'
    assert log_entry['http']['response']['status_code'] == 404
    assert log_entry['url']['path'] == path


def test_404_logging_with_query(client, caplog, configure_logger):
    path = '/api/v1/trigger-not-found'
    client.get(path + '?foo=bar')

    log_entry = json.loads(caplog.text)

    assert log_entry['log.level'] == 'warning'
    assert log_entry['message'] == f'Response 404 on {path}'
    assert log_entry['http']['request']['method'] == 'GET'
    assert log_entry['http']['response']['status_code'] == 404
    assert log_entry['url']['path'] == path


def test_404_logging_post(client, caplog, configure_logger):
    path = '/api/v1/trigger-not-found-post'
    client.post(path)

    log_entry = json.loads(caplog.text)

    assert log_entry['log.level'] == 'warning'
    assert log_entry['message'] == f'Response 404 on {path}'
    assert log_entry['http']['request']['method'] == 'POST'
    assert log_entry['http']['response']['status_code'] == 404
    assert log_entry['url']['path'] == path


def test_ninja_validation_logging(client, caplog, configure_logger):
    path = '/api/v1/trigger-ninja-validation-error'
    client.get(path)

    log_entry = json.loads(caplog.text)

    assert log_entry['log.level'] == 'warning'
    assert log_entry['message'] == f'Response 422 on {path}'
    assert log_entry['http']['request']['method'] == 'GET'
    assert log_entry['http']['response']['status_code'] == 422
    assert log_entry['url']['path'] == path


def test_500_server_error_logging(client, caplog, configure_logger):
    path = '/api/v1/trigger-internal-server-error'
    client.get(path)

    # we need to split the caplog, since I can't get rid of the bloody
    # django.log which also logs the request
    log_entry = json.loads(caplog.text.split('\n')[0])

    assert log_entry['log.level'] == 'error'
    assert log_entry['message'] == 'RuntimeError()'
    assert log_entry['http']['response']['status_code'] == 500
    assert 'error' in log_entry
    assert 'stack_trace' in log_entry['error']
    assert 'raise RuntimeError()' in log_entry['error']['stack_trace']
    assert log_entry['url']['path'] == path


def test_http_error_logging(client, caplog, configure_logger):
    path = '/api/v1/trigger-http-error'
    response = client.get(path)

    # we need to split the caplog, since I can't get rid of the bloody
    # django.log which also logs the request
    log_entry = json.loads(caplog.text.split('\n')[0])

    assert log_entry['log.level'] == 'info'
    assert log_entry['http']['response']['status_code'] == 303
    assert log_entry['message'] == f"Response 303 on {path}"
    assert log_entry['url']['path'] == path


def test_positive_request_log(client, caplog, configure_logger):
    path = '/api/v1/trigger-200-response'
    response = client.get(path)

    # we need to split the caplog, since I can't get rid of the bloody
    # django.log which also logs the request
    log_entry = json.loads(caplog.text.split('\n')[0])

    assert log_entry['message'] == f'Response 200 on {path}'
    assert log_entry['http']['request']['method'] == "GET"
    assert log_entry['http']['response']['status_code'] == 200
    assert log_entry['url']['path'] == path
