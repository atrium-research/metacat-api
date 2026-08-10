import tests


def test_no_auth(client):
    response = client.get("/harvest/tasks")
    assert response.status_code == 401


def test_bad_header(client):
    client.headers["x-api-key"] = "false_key"
    response = client.get("/harvest/tasks")
    assert response.status_code == 401


def test_header_ok(client):
    client.headers["x-api-key"] = tests.api_key
    response = client.get("/harvest/tasks")
    assert response.status_code == 200


def test_bad_param(client):
    response = client.get("/harvest/tasks", params={"api_key": "false_key"})
    assert response.status_code == 401


def test_param_ok(client):
    response = client.get("/harvest/tasks", params={"api_key": tests.api_key})
    assert response.status_code == 200


def test_client_auth_ok(client_auth):
    response = client_auth.get("/harvest/tasks")
    assert response.status_code == 200
