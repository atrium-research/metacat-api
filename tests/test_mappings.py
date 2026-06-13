def test_list_mappings(client):
    response = client.get("/v1/mappings")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_filter_mappings_by_relation(client):
    response = client.get("/v1/mappings?relation=exactMatch")
    assert response.status_code == 200
    assert all(m["relation"] == "exactMatch" for m in response.json())


def test_overlap(client):
    response = client.get("/v1/mappings/overlap?vocab_a=getty-aat&vocab_b=lcsh")
    assert response.status_code == 200
    body = response.json()
    assert body["shared_concepts"] >= 1
    assert body["total_a"] > 0
    assert body["total_b"] > 0


def test_overlap_requires_both_vocabularies(client):
    response = client.get("/v1/mappings/overlap?vocab_a=getty-aat")
    assert response.status_code == 422
