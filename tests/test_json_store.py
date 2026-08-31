import pytest

from metacat_api.config import settings
from metacat_api.datasources.store import set_store, store
from metacat_api.services.facets import update_all_facet_values


def test_default_store():
    set_store(settings.json_data_dir)
    assert len(store.catalogues) == 4
    assert store.vocabularies
    assert not store.facet_values


def test_json_store_reads_directory():
    set_store(settings.json_data_dir)
    assert len(store.catalogues) == 4
    assert not store.facet_values
    update_all_facet_values()
    assert store.facet_values


@pytest.fixture
def empty_store():
    set_store("/nonexistent/metacat/data")
    yield
    set_store(settings.json_data_dir)


def test_json_store_missing_directory_is_empty(empty_store):
    assert store.catalogues == []
