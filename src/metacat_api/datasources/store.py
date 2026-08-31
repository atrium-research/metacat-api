import json
import logging
from pathlib import Path
from uuid import UUID

import anyio
from pydantic_core import to_jsonable_python

from metacat_api.config import settings
from metacat_api.models import (
    Collection,
    CollectionValues,
    Store,
)

logger = logging.getLogger(__name__)


def _read(file_path: Path) -> CollectionValues:
    if not file_path.exists():
        logger.warning(f"Path does not exist: {file_path}")
        return []
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def _read_last_facet_values(json_data_dir: str) -> CollectionValues:
    path = Path(json_data_dir) / Collection.facet_values
    facet_values = [fv for file in path.glob("**/*.json") for fv in _read(file)]
    return facet_values


def _read_store(json_data_dir: str) -> Store:
    path = Path(json_data_dir)
    static_files = [Collection.catalogues, Collection.catalogues_versions, Collection.vocabularies]
    loaded = {name: _read(path / f"{name}.json") for name in static_files}
    loaded[Collection.facet_values] = _read_last_facet_values(json_data_dir)
    return Store.model_validate(
        loaded,
        extra="forbid",
    )


store = _read_store(settings.json_data_dir)


def set_store(json_data_dir: str):
    store.update(_read_store(json_data_dir))


async def update_catalogue_version():
    file = settings.json_data_path() / f"{Collection.catalogues_versions}.json"
    async with await anyio.open_file(file, "w", encoding="utf-8") as handle:
        await handle.write(
            json.dumps(
                store.catalogues_versions,
                indent=2,
                ensure_ascii=False,
                default=to_jsonable_python,
            )
        )
        await handle.write("\n")


async def write_facet_values(catalogue_id: str, version_id: UUID):
    folder = anyio.Path(settings.json_data_path() / Collection.facet_values / catalogue_id)
    await folder.mkdir(parents=True, exist_ok=True)

    data = [fv for fv in store.facet_values if fv.catalogue_id == catalogue_id and fv.version_id == version_id]
    async with await anyio.open_file(folder / f"{version_id}.json", "w", encoding="utf-8") as handle:
        await handle.write(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                default=to_jsonable_python,
            )
        )
        await handle.write("\n")
