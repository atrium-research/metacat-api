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


def test_facet_values_carry_timestamp(client):
    response = client.get("/v1/facets/resource-type/values?catalogues=ariadne")
    assert response.status_code == 200
    values = response.json()
    assert values
    assert all(v["catalogue_id"] == "ariadne" for v in values)
    assert all(v["timestamp"] for v in values)


def test_compare_marks_gap_as_null(client):
    response = client.get("/v1/facets/discipline/compare?catalogues=ariadne,gotriple")
    assert response.status_code == 200
    body = response.json()
    rows = {row["value"]: row["counts"] for row in body["values"]}
    assert rows["Archaeology"]["ariadne"] == 3142897
    assert rows["Archaeology"]["gotriple"] is None


def test_timeseries_returns_monthly_points(client):
    response = client.get("/v1/facets/resource-type/timeseries?catalogues=gotriple")
    assert response.status_code == 200
    points = response.json()
    assert len(points) == 24
    assert all(p["catalogue_id"] == "gotriple" for p in points)


def test_invalid_facet_returns_validation_error(client):
    response = client.get("/v1/facets/not-a-facet/values")
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
