from metacat_api.config import settings
from metacat_api.datasources.store import read_store


def test_json_store_reads_directory():
    datasource = read_store(settings.json_data_dir)
    assert len(datasource.catalogues) == 4
    assert datasource.facet_values
    assert datasource.facet_timeseries


def test_json_store_missing_directory_is_empty():
    datasource = read_store("/nonexistent/metacat/data")
    assert datasource.catalogues == []
    assert datasource.facet_timeseries == []
