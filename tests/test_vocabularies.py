def test_list_vocabularies(client):
    response = client.get("/v1/vocabularies")
    assert response.status_code == 200
    assert any(v["id"] == "getty-aat" for v in response.json())


def test_get_vocabulary(client):
    response = client.get("/v1/vocabularies/getty-aat")
    assert response.status_code == 200
    assert response.json()["authority"] == "Getty Research Institute"


def test_unknown_vocabulary_returns_error_envelope(client):
    response = client.get("/v1/vocabularies/nope")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
