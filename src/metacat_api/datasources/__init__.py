from functools import lru_cache

from metacat_api.config import Datasource as DatasourceKind
from metacat_api.config import settings
from metacat_api.datasources.base import Datasource
from metacat_api.datasources.json_store import JsonStoreDatasource
from metacat_api.datasources.mock import MockDatasource
from metacat_api.datasources.sparql import SparqlDatasource


@lru_cache
def get_datasource() -> Datasource:
    if settings.datasource is DatasourceKind.json:
        return JsonStoreDatasource(settings.json_data_dir)
    if settings.datasource is DatasourceKind.sparql:
        return SparqlDatasource(settings.sparql_endpoint)
    return MockDatasource()
