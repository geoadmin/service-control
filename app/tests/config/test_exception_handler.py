import mock_api  # pylint: disable=unused-import


def test_handle_404_not_found(client):
    response = client.get('/api/v1/trigger-not-found')
    assert response.status_code == 404
    assert response.json() == {'code': 404, 'description': 'Resource not found'}


def test_handle_does_not_exist(client, db):
    response = client.get('/api/v1/trigger-does-not-exist')
    assert response.status_code == 404
    assert response.json() == {'code': 404, 'description': 'Resource not found'}


def test_handle_http_error(client):
    response = client.get('/api/v1/trigger-http-error')
    assert response.status_code == 303
    assert response.json() == {'code': 303, 'description': 'See other'}


def test_handle_ninja_validation_error(client):
    response = client.get('/api/v1/trigger-ninja-validation-error')
    assert response.status_code == 422
    assert response.json() == {'code': 422, 'description': ['Not a valid email.']}


def test_handle_unauthorized(client):
    response = client.get('/api/v1/trigger-authentication-error')
    assert response.status_code == 401
    assert response.json() == {'code': 401, 'description': 'Unauthorized'}


def test_handle_exception(client):
    response = client.get('/api/v1/trigger-internal-server-error')
    assert response.status_code == 500
    assert response.json() == {'code': 500, 'description': 'Internal Server Error'}


def test_handle_django_validation_error(client):
    response = client.get('/api/v1/trigger-django-validation-error')
    assert response.status_code == 422
    assert response.json() == {'code': 422, 'description': ['Not a valid email.']}


def test_handle_cognito_connection_error(client):
    response = client.get('/api/v1/trigger-cognito-connection-error')
    assert response.status_code == 503
    assert response.json() == {'code': 503, 'description': 'Service Unavailable'}
