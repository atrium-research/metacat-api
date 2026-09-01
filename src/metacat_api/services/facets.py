import logging
from datetime import datetime

from metacat_api.config import settings
from metacat_api.datasources.store import read_facet_values, store
from metacat_api.models import CatalogueVersion, FacetId, FacetValue, FacetValuesSort, FacetValuesSortDirection
from metacat_api.services.catalogues import get_last_catalogues_version

logger = logging.getLogger(__name__)


def list_facets() -> list[FacetId]:
    return list(FacetId)


def _update_facet_values(catalogue_version: CatalogueVersion):
    new_facet_values = read_facet_values(
        settings.json_data_dir,
        catalogue_version.catalogue_id,
        catalogue_version.version_id,
    )
    store.update_facet_values(catalogue_version.catalogue_id, new_facet_values)


def update_all_facet_values():
    logger.info("Start update_all_facet_values")
    start = datetime.now()
    for lv in get_last_catalogues_version():
        _update_facet_values(lv)
    logger.info(f"End update_all_facet_values in {datetime.now() - start}, facet values: {len(store.facet_values)}")


def catalogue_facet_values(catalogue_id: str) -> list[FacetValue]:
    if not store.facet_values:
        update_all_facet_values()
    return [fv for fv in store.facet_values if fv.catalogue_id == catalogue_id]


def _sort(
    facet_values: list[FacetValue],
    sort: FacetValuesSort,
    direction: FacetValuesSortDirection,
) -> list[FacetValue]:
    reverse = direction == FacetValuesSortDirection.desc
    match sort:
        case FacetValuesSort.facet:
            return sorted(facet_values, key=lambda fv: fv.facet, reverse=reverse)
        case FacetValuesSort.value:
            return sorted(facet_values, key=lambda fv: fv.value, reverse=reverse)
        case FacetValuesSort.count:
            return sorted(facet_values, key=lambda fv: fv.count, reverse=reverse)
        case _:
            return facet_values


def facet_values(
    facets: list[FacetId] | None = None,
    catalogues: list[str] | None = None,
    sort: FacetValuesSort | None = None,
    direction: FacetValuesSortDirection = FacetValuesSortDirection.asc,
) -> list[FacetValue]:
    if not store.facet_values:
        update_all_facet_values()
    filtered_facet_values = [
        fv
        for fv in store.facet_values
        if (not facets or fv.facet in facets) and (not catalogues or fv.catalogue_id in catalogues)
    ]
    return _sort(filtered_facet_values, sort, direction)
