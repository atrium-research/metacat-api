from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from metacat_api.models import FacetComparison, FacetId, FacetTimeseriesPoint, FacetValue
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown catalogues: '{unknown_catalogues}'")
    return selected_catalogues


_catalogues_query = Annotated[
    str | None,
    Depends(_parse_catalogues),
    Query(description="Comma-separated catalogue identifiers to restrict the result."),
]


@router.get("", summary="List the facets")
def list_facets() -> list[FacetId]:
    return facets_service.list_facets()


def _to_utc(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    return dt.replace(tzinfo=UTC)


@router.get(
    "/{facet}/values",
    summary="Facet values with counts and timestamps",
)
def facet_values(
    facet: FacetId,
    catalogues: _catalogues_query = None,
    date_from: Annotated[datetime | None, Query(alias="from")] = None,
    date_to: Annotated[datetime | None, Query(alias="to")] = None,
) -> list[FacetValue]:
    return facets_service.facet_values(facet, _parse_catalogues(catalogues), _to_utc(date_from), _to_utc(date_to))


@router.get(
    "/{facet}/compare",
    summary="Transversal side-by-side comparison across catalogues",
)
def facet_compare(
    facet: FacetId,
    catalogues: _catalogues_query = None,
) -> FacetComparison:
    return facets_service.facet_compare(facet, _parse_catalogues(catalogues))


@router.get(
    "/{facet}/timeseries",
    summary="Evolution of a facet over time",
)
def facet_timeseries(
    facet: FacetId,
    catalogues: _catalogues_query = None,
    date_from: Annotated[datetime | None, Query(alias="from")] = None,
    date_to: Annotated[datetime | None, Query(alias="to")] = None,
) -> list[FacetTimeseriesPoint]:
    return facets_service.facet_timeseries(facet, _parse_catalogues(catalogues), _to_utc(date_from), _to_utc(date_to))
