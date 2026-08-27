from uuid import UUID

from metacat_api.datasources.store import store
from metacat_api.models import Catalogue, CatalogueVersion


def list_catalogues() -> list[Catalogue]:
    return store.catalogues


def get_catalogue(catalogue_id: str) -> Catalogue | None:
    return next((c for c in store.catalogues if c.id == catalogue_id), None)


def list_catalogue_versions(catalogue_id: str) -> list[CatalogueVersion]:
    return [v for v in store.catalogues_versions if v.catalogue_id == catalogue_id]


def get_catalogue_version(catalogue_id: str, version_id: UUID) -> CatalogueVersion | None:
    return next(
        (v for v in store.catalogues_versions if v.catalogue_id == catalogue_id and v.version_id == version_id), None
    )


def get_last_catalogue_version(catalogue_id: str) -> CatalogueVersion | None:
    versions = list_catalogue_versions(catalogue_id)
    if not versions:
        return None
    return max(versions, key=lambda v: v.harvest_at)
