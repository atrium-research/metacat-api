from metacat_api.config import settings
from metacat_api.datasources.store import set_store


def test_list_catalogues(client):
    response = client.get("/v1/catalogues")
    assert response.status_code == 200
    catalogues = response.json()
    assert {c["id"] for c in catalogues} == {"ariadne", "clarin-vlo", "gotriple", "sshomp"}


def test_get_catalogue(client):
    response = client.get("/v1/catalogues/clarin-vlo")
    assert response.status_code == 200
    assert response.json()["domain"] == "Linguistics"


def test_get_catalogue_version(client):
    response = client.get("/v1/catalogues/clarin-vlo/versions/228608b7-f3fb-4b9d-883d-1ae94d2b92b9")
    assert response.status_code == 200
    assert response.json()["total_resources"] == 2285870


def test_unknown_catalogue_returns_error_envelope(client):
    response = client.get("/v1/catalogues/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
    assert "detail" in body


def test_catalogue_facets_returns_six(client):
    response = client.get("/v1/catalogues/ariadne/versions/last")
    assert response.status_code == 200
    catalogue_version = response.json()
    assert len(catalogue_version["facet_exposures"]) == 6


def test_gap_is_reported_explicitly(client):
    response = client.get("/v1/catalogues/gotriple/versions/last")
    facet_format = next(f for f in response.json()["facet_exposures"] if f["facet"] == "format")
    assert facet_format
    assert facet_format["status"] == "gap"
    assert facet_format["reason"]
    assert facet_format["total_count"] is None


def test_facet_coverage_is_compact(client):
    response = client.get("/v1/catalogues/ariadne/versions/last")
    assert response.status_code == 200
    catalogue_version = response.json()
    assert len(catalogue_version["facet_exposures"]) == 6
    fe_discipline = next(fe for fe in catalogue_version["facet_exposures"] if fe["facet"] == "discipline")
    assert fe_discipline
    assert fe_discipline["status"] == "implicit"


def test(client):

    response = client.get("/v1/catalogues")
    assert response.status_code == 200
    catalogues = response.json()
    assert catalogues
    assert {c["id"] for c in catalogues} == {"ariadne", "clarin-vlo", "gotriple", "sshomp"}

    set_store("nonexistent")

    response = client.get("/v1/catalogues")
    assert response.status_code == 200
    catalogues = response.json()
    assert not catalogues

    set_store(settings.json_data_dir)

    response = client.get("/v1/catalogues")
    assert response.status_code == 200
    catalogues = response.json()
    assert catalogues
    assert {c["id"] for c in catalogues} == {"ariadne", "clarin-vlo", "gotriple", "sshomp"}
