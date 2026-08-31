from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import (
    Catalogue,
    CatalogueVersion,
    ErrorResponse,
    FacetValue,
)
from metacat_api.services import catalogues as service
from metacat_api.services.facets import facet_values

router = APIRouter(prefix="/catalogues", tags=["Catalogues"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


def _require_catalogue(catalogue_id: str) -> Catalogue:
    catalogue = service.get_catalogue(catalogue_id)
    if not catalogue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown catalogue '{catalogue_id}'")
    return catalogue


required_catalogue = Annotated[Catalogue, Depends(_require_catalogue)]


def _require_catalogue_version(catalogue_id: str, version_id: UUID) -> CatalogueVersion:
    _require_catalogue(catalogue_id)
    catalogue_version = service.get_catalogue_version(catalogue_id, version_id)
    if not catalogue_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown catalogue version '{version_id}'")
    return catalogue_version


required_catalogue_version = Annotated[CatalogueVersion, Depends(_require_catalogue_version)]


def _require_last_catalogue_version(catalogue_id: str) -> CatalogueVersion:
    _require_catalogue(catalogue_id)
    last_version = service.get_last_catalogue_version(catalogue_id)
    if not last_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No last version")
    return last_version


required_last_catalogue_version = Annotated[CatalogueVersion, Depends(_require_last_catalogue_version)]


@router.get("", summary="List all catalogues")
def list_catalogues() -> list[Catalogue]:
    return service.list_catalogues()


@router.get(
    "/{catalogue_id}",
    responses=_NOT_FOUND,
    summary="Single catalogue detail",
    dependencies=[Depends(_require_catalogue)],
)
def get_catalogue(catalogue_id: str, catalogue: required_catalogue) -> Catalogue:
    return catalogue


@router.get(
    "/{catalogue_id}/versions",
    responses=_NOT_FOUND,
    summary="Catalogue versions",
    dependencies=[Depends(_require_catalogue)],
)
def catalogue_versions(catalogue_id: str) -> list[CatalogueVersion]:
    return service.list_catalogue_versions(catalogue_id)


@router.get(
    "/{catalogue_id}/versions/last",
    responses=_NOT_FOUND,
    summary="Last catalogue version",
    dependencies=[Depends(_require_last_catalogue_version)],
)
def catalogue_version_last(
    catalogue_id: str, last_catalogue_version: required_last_catalogue_version
) -> CatalogueVersion:
    return last_catalogue_version


@router.get(
    "/{catalogue_id}/versions/{version_id}",
    responses=_NOT_FOUND,
    summary="Single catalogue version",
    dependencies=[Depends(_require_catalogue_version)],
)
def catalogue_version_by_id(
    catalogue_id: str, version_id: UUID, catalogue_version: required_catalogue_version
) -> CatalogueVersion:
    return catalogue_version


@router.get(
    "/{catalogue_id}/versions/last/facet_values",
    summary="Facet values",
    dependencies=[Depends(_require_last_catalogue_version)],
)
def catalogue_last_facet_values(catalogue_id: str) -> list[FacetValue]:
    return facet_values(catalogues=[catalogue_id])
