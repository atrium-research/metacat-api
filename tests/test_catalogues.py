def test_list_catalogues(client):
    response = client.get("/v1/catalogues")
    assert response.status_code == 200
    catalogues = response.json()
    assert {c["id"] for c in catalogues} == {"ariadne", "clarin-vlo", "gotriple", "sshomp"}


def test_get_catalogue(client):
    response = client.get("/v1/catalogues/ariadne")
    assert response.status_code == 200
    assert response.json()["total_resources"] == 3142897


def test_unknown_catalogue_returns_error_envelope(client):
    response = client.get("/v1/catalogues/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
    assert "detail" in body


def test_catalogue_facets_returns_six(client):
    response = client.get("/v1/catalogues/ariadne/facets")
    assert response.status_code == 200
    facets = response.json()
    assert len(facets) == 6


def test_gap_is_reported_explicitly(client):
    response = client.get("/v1/catalogues/gotriple/facets")
    facets = {f["facet"]: f for f in response.json()}
    assert facets["format"]["status"] == "gap"
    assert facets["format"]["reason"]
    assert facets["format"]["total_count"] is None


def test_facet_coverage_is_compact(client):
    response = client.get("/v1/catalogues/ariadne/facet-coverage")
    assert response.status_code == 200
    coverage = response.json()
    assert coverage["discipline"] == "implicit"
    assert len(coverage) == 6
