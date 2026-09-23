import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from metacat_api.services.auth import is_api_key_valid
from metacat_api.services.export import ExportError, read_ao_cat, update_ao_cat

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


@router.get(
    "/ao-cat",
    summary="Export data to AO-Cat format",
)
async def get_export_ao_cat():
    try:
        ao_cat = await read_ao_cat()

    except ExportError as e:
        logger.exception("Export read error")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Unable to read AO-Cat") from e

    return Response(
        content=ao_cat,
        media_type="text/turtle",
        headers={"Content-Disposition": 'attachment; filename="ao_cat.ttl"'},
    )


@router.post(
    "/ao-cat",
    summary="Update AO-Cat: recompute and write ttl",
    dependencies=[Depends(is_api_key_valid)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def post_update_ao_cat():
    try:
        await update_ao_cat()
    except ExportError as e:
        logger.exception("Export update error")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Unable to update AO-Cat") from e
