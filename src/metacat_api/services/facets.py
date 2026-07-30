from datetime import datetime

from metacat_api.datasources.base import Datasource
from metacat_api.models.common import PivotFacet
from metacat_api.models.facet import (
    FacetComparison,
    FacetComparisonRow,
    FacetTimeseriesPoint,
    FacetValue,
)

CATALOGUE_ORDER = ["ariadne", "clarin-vlo", "gotriple", "sshomp"]


def list_facets() -> list[str]:
    return [facet.value for facet in PivotFacet]


def facet_values(
    ds: Datasource,
    facet: PivotFacet,
    catalogues: list[str] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[FacetValue]:
    result = []
    for value in ds.facet_values():
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


def facet_timeseries(
    ds: Datasource,
    facet: PivotFacet,
    catalogues: list[str] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[FacetTimeseriesPoint]:
    result = []
    for point in ds.facet_timeseries():
        if point.facet != facet:
            continue
        if catalogues and point.catalogue_id not in catalogues:
            continue
        if date_from and point.timestamp < date_from:
            continue
        if date_to and point.timestamp > date_to:
            continue
        result.append(point)
    return result


def facet_compare(
    ds: Datasource,
    facet: PivotFacet,
    catalogues: list[str] | None = None,
) -> FacetComparison:
    facet_all = [v for v in ds.facet_values() if v.facet == facet]
    if catalogues:
        selected = list(catalogues)
    else:
        present = {v.catalogue_id for v in facet_all}
        selected = [c for c in CATALOGUE_ORDER if c in present] or sorted(present)

    latest = max((v.timestamp for v in facet_all), default=None)
    latest_values = [v for v in facet_all if v.timestamp == latest]

    counts_by_value: dict[str, dict[str, int]] = {}
    for value in latest_values:
        if value.catalogue_id in selected:
            counts_by_value.setdefault(value.value, {})[value.catalogue_id] = value.count

    rows = [
        FacetComparisonRow(
            value=value,
            counts={catalogue: counts.get(catalogue) for catalogue in selected},
        )
        for value, counts in sorted(
            counts_by_value.items(),
            key=lambda item: max(item[1].values()),
            reverse=True,
        )
    ]

    return FacetComparison(
        facet=facet,
        catalogues=selected,
        snapshot_timestamp=latest,
        values=rows,
    )
