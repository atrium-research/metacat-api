def test_list_facets(client):
    response = client.get("/v1/facets")
    assert response.status_code == 200
    facets = response.json()
    assert facets == [
        "resource-type",
        "format",
        "discipline",
        "source",
        "source-2",
        "subjects",
    ]


def test_facet_values_no_timestamp(client):
    response = client.get("/v1/facets/resource-type/values?catalogues=ariadne")
    assert response.status_code == 200
    values = response.json()
    assert values
    assert all(v["catalogue_id"] == "ariadne" for v in values)
    assert all("timestamp" not in v for v in values)


def test_invalid_facet_returns_validation_error(client):
    response = client.get("/v1/facets/not-a-facet/values")
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
