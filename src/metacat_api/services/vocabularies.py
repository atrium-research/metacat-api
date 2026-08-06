from metacat_api.datasources.json_store import datasource
from metacat_api.models.vocabulary import Concept, Vocabulary


def list_vocabularies() -> list[Vocabulary]:
    return datasource.vocabularies()


def get_vocabulary(vocabulary_id: str) -> Vocabulary | None:
    return next((v for v in datasource.vocabularies() if v.id == vocabulary_id), None)


def vocabulary_concepts(vocabulary_id: str, offset: int, limit: int) -> tuple[list[Concept], int]:
    concepts = [c for c in datasource.concepts() if c.vocabulary_id == vocabulary_id]
    return concepts[offset : offset + limit], len(concepts)
