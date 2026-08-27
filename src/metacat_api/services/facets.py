from datetime import datetime

from metacat_api.datasources.store import store
from metacat_api.models import FacetId, FacetValue


def list_facets() -> list[FacetId]:
    return list(FacetId)


def facet_values(
    facet: FacetId,
    catalogues: list[str],
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[FacetValue]:
    result = []
    for value in store.facet_values:
        if value.facet != facet:
            continue
        if catalogues and value.catalogue_id not in catalogues:
            continue
        if date_from and value.timestamp < date_from:
            continue
        if date_to and value.timestamp > date_to:
            continue
        result.append(value)
    return result
