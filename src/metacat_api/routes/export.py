import logging

from fastapi import APIRouter, HTTPException, Response, status

from metacat_api.services.export import ExportError, get_current_ao_cat

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


@router.get(
    "/ao-cat",
    summary="Export data to AO-Cat format",
)
async def get_export_ao_cat():
    try:
        ao_cat = get_current_ao_cat()

    except ExportError as e:
        logger.exception(f"Export error: {str(e)}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Unable to export to AO-Cat") from e

    return Response(
        content=ao_cat,
        media_type="text/turtle",
        headers={"Content-Disposition": 'attachment; filename="ao_cat.ttl"'},
    )
