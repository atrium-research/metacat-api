from metacat_api.config import settings
from metacat_api.datasources.store import read_facet_values, store
from metacat_api.models import CatalogueVersion, FacetId, FacetValue
from metacat_api.services.catalogues import get_last_catalogues_version


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
    for lv in get_last_catalogues_version():
        _update_facet_values(lv)


def catalogue_facet_values(catalogue_id: str) -> list[FacetValue]:
    if not store.facet_values:
        update_all_facet_values()
    return [fv for fv in store.facet_values if fv.catalogue_id == catalogue_id]


def facet_values(
    facets: list[FacetId] | None = None,
    catalogues: list[str] | None = None,
) -> list[FacetValue]:
    if not store.facet_values:
        update_all_facet_values()
    return [
        fv
        for fv in store.facet_values
        if (not facets or fv.facet in facets) and (not catalogues or fv.catalogue_id in catalogues)
    ]
