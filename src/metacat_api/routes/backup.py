from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import ErrorResponse
from metacat_api.models.backup import BackupInfo
from metacat_api.services.auth import is_api_key_valid
from metacat_api.services.backup import BackupError, read_backup, write_backup

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.get(
    "/last-update-info",
    dependencies=[Depends(is_api_key_valid)],
)
async def get_last_update_info() -> BackupInfo:
    try:
        return await read_backup()
    except BackupError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Unable to get last update: {str(e)}") from e


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
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Unable to create backup: {str(e)}") from e
