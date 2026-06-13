from metacat_api.datasources.base import Datasource
from metacat_api.models.vocabulary import Concept, Vocabulary


def list_vocabularies(ds: Datasource) -> list[Vocabulary]:
    return ds.vocabularies()


def get_vocabulary(ds: Datasource, vocabulary_id: str) -> Vocabulary | None:
    return next((v for v in ds.vocabularies() if v.id == vocabulary_id), None)


def vocabulary_concepts(
    ds: Datasource, vocabulary_id: str, offset: int, limit: int
) -> tuple[list[Concept], int]:
    concepts = [c for c in ds.concepts() if c.vocabulary_id == vocabulary_id]
    return concepts[offset : offset + limit], len(concepts)
