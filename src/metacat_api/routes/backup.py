import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from metacat_api.models import ErrorResponse
from metacat_api.models.backup import BackupInfo
from metacat_api.services.auth import is_api_key_valid
from metacat_api.services.backup import GIT_PAGE, BackupError, read_backup, write_backup

router = APIRouter(prefix="/backup", tags=["Backup"])

logger = logging.getLogger(__name__)


@router.get(
    "/last-update-info",
    dependencies=[Depends(is_api_key_valid)],
)
async def get_last_update_info() -> BackupInfo:
    try:
        return await read_backup()
    except BackupError as e:
        logger.exception(f"Backup error: {str(e)}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Unable to get last update") from e


@router.get("/page", response_class=RedirectResponse, status_code=301)
async def get_page():
    return GIT_PAGE


@router.post(
    "/create-backup",
    dependencies=[Depends(is_api_key_valid)],
    responses={
        status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponse},
    },
)
async def post_create_backup() -> BackupInfo:
    try:
        return await write_backup()
    except BackupError as e:
        logger.exception(f"Backup error: {str(e)}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Unable to create backup") from e
