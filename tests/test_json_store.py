from metacat_api.config import settings
from metacat_api.datasources.json_store import JsonStoreDatasource


def test_json_store_reads_directory():
    ds = JsonStoreDatasource(settings.mock_data_dir)
    assert len(ds.catalogues()) == 4
    assert ds.facet_values()
    assert ds.facet_timeseries()


def test_json_store_missing_directory_is_empty():
    ds = JsonStoreDatasource("/nonexistent/metacat/data")
    assert ds.catalogues() == []
    assert ds.facet_timeseries() == []
