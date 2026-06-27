from pathlib import Path

from metacat_api.datasources.json_store import JsonStoreDatasource

MOCK_DIR = Path(__file__).resolve().parents[1] / "src" / "metacat_api" / "mock_data"


def test_json_store_reads_directory():
    ds = JsonStoreDatasource(str(MOCK_DIR))
    assert len(ds.catalogues()) == 4
    assert ds.facet_values()
    assert ds.facet_timeseries()


def test_json_store_missing_directory_is_empty():
    ds = JsonStoreDatasource("/nonexistent/metacat/data")
    assert ds.catalogues() == []
    assert ds.facet_timeseries() == []
