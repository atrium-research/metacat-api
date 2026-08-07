from metacat_api.config import settings
from metacat_api.datasources.store import set_store, store


def test_json_store_reads_directory():
    set_store(settings.json_data_dir)
    assert len(store.catalogues) == 4
    assert store.facet_values
    assert store.facet_timeseries


def test_json_store_missing_directory_is_empty():
    set_store("/nonexistent/metacat/data")
    assert store.catalogues == []
    assert store.facet_timeseries == []
