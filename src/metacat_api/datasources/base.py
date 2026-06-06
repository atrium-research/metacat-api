from abc import ABC, abstractmethod

from metacat_api.models.catalogue import Catalogue
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary


class Datasource(ABC):
    """Read contract every backend must satisfy.

    Backends return whole collections. Filtering, pagination and
    cross-catalogue aggregation live in the service layer.
    """

    @abstractmethod
    def catalogues(self) -> list[Catalogue]: ...

    @abstractmethod
    def facet_exposures(self) -> list[FacetExposure]: ...

    @abstractmethod
    def facet_values(self) -> list[FacetValue]: ...

    @abstractmethod
    def facet_timeseries(self) -> list[FacetTimeseriesPoint]: ...

    @abstractmethod
    def vocabularies(self) -> list[Vocabulary]: ...

    @abstractmethod
    def concepts(self) -> list[Concept]: ...

    @abstractmethod
    def mappings(self) -> list[Mapping]: ...

    @abstractmethod
    def snapshots(self) -> list[Snapshot]: ...
