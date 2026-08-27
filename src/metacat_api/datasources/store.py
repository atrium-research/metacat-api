import json
import logging
from pathlib import Path

from pydantic_core import to_jsonable_python

from metacat_api.config import settings
from metacat_api.models import (
    Collection,
    CollectionValues,
    Store,
)

logger = logging.getLogger(__name__)


def _read(directory: Path, name: str) -> CollectionValues:
    file_path = directory / f"{name}.json"
    if not file_path.exists():
        logger.warning(f"Path does not exist: {file_path}")
        return []
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def _read_store(json_data_dir: str) -> Store:
    path = Path(json_data_dir)
    loaded = {name: _read(path, name) for name in Collection}
    return Store.model_validate(
        loaded,
        extra="forbid",
    )


store = _read_store(settings.json_data_dir)


def set_store(json_data_dir: str):
    store.update(_read_store(json_data_dir))


def write_store() -> None:
    for name in [Collection.catalogues_versions, Collection.facet_values]:
        with open(settings.json_data_path() / f"{name}.json", "w", encoding="utf-8") as handle:
            json.dump(store.get(name), handle, indent=2, ensure_ascii=False, default=to_jsonable_python)
            handle.write("\n")
