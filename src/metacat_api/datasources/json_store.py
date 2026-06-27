import json
from collections import defaultdict
from pathlib import Path

from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary


class JsonStoreDatasource(Datasource):
    """Reads timestamped JSON snapshots from the metacat-data store.

    Expects a directory holding the metacat-data layout (one file per
    collection). Missing files are treated as empty collections so a
    partially populated store still serves. The store is produced by the
    harvesting connectors in metacat-code (see scripts/harvest_clarin.py).
    """

    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
        self._catalogues = [Catalogue(**item) for item in self._read("catalogues.json")]
        self._facet_exposures = [
            FacetExposure(**item) for item in self._read("facet_exposures.json")
        ]
        self._facet_values = [FacetValue(**item) for item in self._read("facet_values.json")]
        self._vocabularies = [Vocabulary(**item) for item in self._read("vocabularies.json")]
        self._concepts = [Concept(**item) for item in self._read("concepts.json")]
        self._mappings = [Mapping(**item) for item in self._read("mappings.json")]
        self._snapshots = [Snapshot(**item) for item in self._read("snapshots.json")]

    def _read(self, name: str) -> list[dict]:
        path = self.data_dir / name
        if not path.exists():
            return []
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

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
