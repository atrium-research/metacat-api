from metacat_api.datasources.store import store
from metacat_api.models import Vocabulary


def list_vocabularies() -> list[Vocabulary]:
    return store.vocabularies


def get_vocabulary(vocabulary_id: str) -> Vocabulary | None:
    return next((v for v in store.vocabularies if v.id == vocabulary_id), None)
