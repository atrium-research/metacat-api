from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from metacat_api.config import DatasourceKind, settings
from metacat_api.datasources.base import Datasource
from metacat_api.datasources.json_store import JsonStoreDatasource
from metacat_api.datasources.sparql import SparqlDatasource


@lru_cache
def get_datasource() -> Datasource:
    if settings.datasource_kind is DatasourceKind.json:
        return JsonStoreDatasource(settings.json_data_dir)
    if settings.datasource_kind is DatasourceKind.sparql:
        return SparqlDatasource(settings.sparql_endpoint)
    raise ValueError(f"Unkown datasource kind: {settings.datasource_kind}")


datasource_dep = Annotated[Datasource, Depends(get_datasource)]
