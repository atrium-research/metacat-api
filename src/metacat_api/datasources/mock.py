import json
from collections import defaultdict
from pathlib import Path

from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary

DATA_DIR = Path(__file__).resolve().parents[1] / "mock_data"


def _load(name: str) -> list[dict]:
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


class MockDatasource(Datasource):
    """Self-sufficient backend serving the bundled mock_data files."""

    def __init__(self) -> None:
        self._catalogues = [Catalogue(**item) for item in _load("catalogues.json")]
        self._facet_exposures = [FacetExposure(**item) for item in _load("facet_exposures.json")]
        self._facet_values = [FacetValue(**item) for item in _load("facet_values.json")]
        self._vocabularies = [Vocabulary(**item) for item in _load("vocabularies.json")]
        self._concepts = [Concept(**item) for item in _load("concepts.json")]
        self._mappings = [Mapping(**item) for item in _load("mappings.json")]
        self._snapshots = [Snapshot(**item) for item in _load("snapshots.json")]

    def catalogues(self) -> list[Catalogue]:
        return self._catalogues

    def facet_exposures(self) -> list[FacetExposure]:
        return self._facet_exposures

    def facet_values(self) -> list[FacetValue]:
        return self._facet_values

    def facet_timeseries(self) -> list[FacetTimeseriesPoint]:
        totals: dict[tuple, int] = defaultdict(int)
        for value in self._facet_values:
            totals[(value.catalogue_id, value.facet, value.timestamp)] += value.count
        points = [
            FacetTimeseriesPoint(
                catalogue_id=catalogue_id,
                facet=facet,
                timestamp=timestamp,
                total_count=total,
            )
            for (catalogue_id, facet, timestamp), total in totals.items()
        ]
        points.sort(key=lambda point: (point.catalogue_id, point.facet.value, point.timestamp))
        return points

    def vocabularies(self) -> list[Vocabulary]:
        return self._vocabularies

    def concepts(self) -> list[Concept]:
        return self._concepts

    def mappings(self) -> list[Mapping]:
        return self._mappings

    def snapshots(self) -> list[Snapshot]:
        return self._snapshots
