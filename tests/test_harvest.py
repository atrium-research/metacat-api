def test_harvest_tasks(client_auth):
    response = client_auth.get("/harvest/tasks")
    assert response.status_code == 200
    assert response.json()
    res = response.json()
    assert res[0]["id"] == "harvest_and_backup"
