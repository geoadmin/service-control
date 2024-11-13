def test_checker_url(client):
    # intentionally not using reverse here as we want to
    # make sure the URL really is /checker
    response = client.get('/checker')
    assert response.status_code == 200
    content = response.json()

    assert 'success' in content
    assert 'message' in content
    assert content['success'] is True
    assert content['message'] == "OK"
