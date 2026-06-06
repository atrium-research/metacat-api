from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary


class SparqlDatasource(Datasource):
    """Queries the MetaCat GraphDB triplestore over SPARQL.

    TODO: implement SPARQL queries against the AO-Cat model on the
    EOSC EU Node GraphDB instance.
    """

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def catalogues(self) -> list[Catalogue]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def facet_exposures(self) -> list[FacetExposure]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def facet_values(self) -> list[FacetValue]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def facet_timeseries(self) -> list[FacetTimeseriesPoint]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def vocabularies(self) -> list[Vocabulary]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def concepts(self) -> list[Concept]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def mappings(self) -> list[Mapping]:
        raise NotImplementedError("sparql datasource not implemented yet")

    def snapshots(self) -> list[Snapshot]:
        raise NotImplementedError("sparql datasource not implemented yet")
