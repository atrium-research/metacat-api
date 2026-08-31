from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from metacat_api.models import FacetId, FacetValue
from metacat_api.services import catalogues as catalogues_service
from metacat_api.services import facets as facets_service

router = APIRouter(prefix="/facets", tags=["Facets"])


def _parse_catalogues(raw: str | None) -> list[str]:
    if not raw:
        return []

    selected_catalogues = [item.strip() for item in raw.split(",") if item.strip()]
    known_catalogues = [catalogue.id for catalogue in catalogues_service.list_catalogues()]
    unknown_catalogues = [catalogue_id for catalogue_id in selected_catalogues if catalogue_id not in known_catalogues]
    if unknown_catalogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown catalogues: '{unknown_catalogues}'",
        )
    return selected_catalogues


def _parse_facets(raw: str | None) -> list[FacetId]:
    if not raw:
        return []

    selected_facets = [item.strip() for item in raw.split(",") if item.strip()]
    unknown_facets = [facet_id for facet_id in selected_facets if facet_id not in FacetId]
    if unknown_facets:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown facets: '{unknown_facets}'",
        )
    return [FacetId.from_str(f) for f in selected_facets]


_catalogues_query = Annotated[
    str | None,
    Depends(_parse_catalogues),
    Query(description="Comma-separated catalogue identifiers to restrict the result."),
]

_facets_query = Annotated[
    str | None,
    Depends(_parse_facets),
    Query(description="Comma-separated facet identifiers to restrict the result."),
]


@router.get("", summary="List the facets")
def list_facets() -> list[FacetId]:
    return facets_service.list_facets()


@router.get("/values", summary="Facet values")
def facet_values(
    facets: _facets_query = None,
    catalogues: _catalogues_query = None,
) -> list[FacetValue]:
    return facets_service.facet_values(_parse_facets(facets), _parse_catalogues(catalogues))
