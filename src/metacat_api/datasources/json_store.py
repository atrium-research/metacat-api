from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary


class JsonStoreDatasource(Datasource):
    """Reads timestamped JSON snapshots from the metacat-data store.

    TODO: implement reads against the metacat-data repository layout.
    """

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir

    def catalogues(self) -> list[Catalogue]:
        raise NotImplementedError("json datasource not implemented yet")

    def facet_exposures(self) -> list[FacetExposure]:
        raise NotImplementedError("json datasource not implemented yet")

    def facet_values(self) -> list[FacetValue]:
        raise NotImplementedError("json datasource not implemented yet")

    def facet_timeseries(self) -> list[FacetTimeseriesPoint]:
        raise NotImplementedError("json datasource not implemented yet")

    def vocabularies(self) -> list[Vocabulary]:
        raise NotImplementedError("json datasource not implemented yet")

    def concepts(self) -> list[Concept]:
        raise NotImplementedError("json datasource not implemented yet")

    def mappings(self) -> list[Mapping]:
        raise NotImplementedError("json datasource not implemented yet")

    def snapshots(self) -> list[Snapshot]:
        raise NotImplementedError("json datasource not implemented yet")
