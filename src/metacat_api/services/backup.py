import logging
import re
import shutil
from datetime import datetime

from anyio import Path, TemporaryDirectory, open_file
from git import GitCommandError, Repo

from metacat_api.config import settings
from metacat_api.models.backup import BackupInfo, DataFile
from metacat_api.services.util import now, time_to_str

GIT_URL = "https://github.com/atrium-research/metacat-api.git"
GIT_BRANCH = "data"

logger = logging.getLogger(__name__)


class BackupError(RuntimeError):
    pass


def _get_repo(tmp_dir: str) -> Repo:
    logger.info("Getting git repo")
    try:
        repo = Repo.clone_from(GIT_URL, tmp_dir, branch=GIT_BRANCH)
    except GitCommandError as e:
        logger.exception(f"Error during git clone: {str(e)}")
        raise BackupError("Unable to clone repo") from e
    return repo


async def _read_readme(repo_dir) -> str:
    path = Path(f"{repo_dir}/README.md")
    if not await path.exists():
        raise BackupError("No README.md")
    async with await open_file(path, encoding="utf-8") as f:
        return await f.read()


async def _get_last_update(repo_dir: str) -> datetime:
    readme = await _read_readme(repo_dir)
    last_update = re.search(r"The dump was updated on ([^.]+)\.", readme)
    if not last_update:
        raise BackupError(f"Unable to read last update from: {readme}")
    last_update_str = last_update.group(1)
    try:
        return datetime.strptime(last_update_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError as e:
        raise BackupError(f"Unable to parse last update: {last_update_str}") from e


async def _get_data_files(repo_dir: str) -> list[DataFile]:
    return [DataFile(name=p.name, size=(await p.stat()).st_size) async for p in Path(f"{repo_dir}/data").iterdir()]


async def _update_last_update(repo_dir: str, update_date_str: str) -> None:
    if not update_date_str:
        raise BackupError("No update date defined")
    logger.info(f"New update date: {update_date_str}")

    readme = await _read_readme(repo_dir)
    new_readme = re.sub(
        r"The dump was updated on ([^.]+)\.",
        f"The dump was updated on {update_date_str}.",
        readme,
    )
    if not new_readme:
        raise BackupError(f"Unable to replace last update from: {readme}")
    async with await open_file(f"{repo_dir}/README.md", mode="w", encoding="utf-8") as fw:
        await fw.write(new_readme)


async def _update_data(repo_dir: str) -> None:
    logger.info("Updating data files")
    current_data_path = Path(settings.json_data_dir)
    git_data_path = Path(f"{repo_dir}/data")
    if not await git_data_path.exists():
        raise BackupError(f"No previous git data folder at {git_data_path}")
    shutil.rmtree(git_data_path)
    await current_data_path.copy_into(repo_dir)


async def read_backup() -> BackupInfo:
    async with TemporaryDirectory(prefix="repo_dir_r_") as repo_dir:
        repo = _get_repo(repo_dir)
        last_update = await _get_last_update(repo_dir)
        data_files = await _get_data_files(repo_dir)
        logger.info(f"Last update: {last_update}, tz = {last_update.tzname()}")
        repo.close()
    return BackupInfo(
        last_update=time_to_str(last_update),
        data_files=data_files,
    )


async def write_backup() -> BackupInfo:
    logger.info("Start write backup")
    async with TemporaryDirectory(prefix="repo_dir_w_") as repo_dir:
        repo = _get_repo(repo_dir)
        await _update_data(repo_dir)

        update_date = time_to_str(now())
        await _update_last_update(repo_dir, update_date)

        logger.info("Saving to remote repo")
        repo.index.add(["README.md", "data/*.json"])
        repo.index.commit(f"Dump at {update_date}")
        origin = repo.remote("origin")
        origin.push()

        repo.close()

        data_files = await _get_data_files(repo_dir)
    return BackupInfo(
        last_update=update_date,
        data_files=data_files,
    )
