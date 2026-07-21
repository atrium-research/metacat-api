from fastapi import APIRouter, Depends, HTTPException

from metacat_api.datasources import get_datasource
from metacat_api.datasources.base import Datasource
from metacat_api.models.common import ErrorResponse
from metacat_api.models.snapshot import Snapshot

router = APIRouter(prefix="/snapshots", tags=["snapshots"])
activity_router = APIRouter(tags=["activity"])


@router.get("", summary="List snapshots")
def list_snapshots(ds: Datasource = Depends(get_datasource)) -> list[Snapshot]:
    return sorted(ds.snapshots(), key=lambda snapshot: snapshot.taken_at)


@router.get(
    "/latest",
    responses={404: {"model": ErrorResponse}},
    summary="Current snapshot metadata",
)
def latest_snapshot(ds: Datasource = Depends(get_datasource)) -> Snapshot:
    snapshots = ds.snapshots()
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshot available")
    return max(snapshots, key=lambda snapshot: snapshot.taken_at)


@activity_router.get(
    "/activity",
    summary="Latest harvest activity per catalogue for the Overview panel",
)
def activity(ds: Datasource = Depends(get_datasource)) -> list[dict]:
    catalogues = sorted(ds.catalogues(), key=lambda catalogue: catalogue.last_harvest_at, reverse=True)
    return [
        {
            "catalogue_id": catalogue.id,
            "name": catalogue.name,
            "last_harvest_at": catalogue.last_harvest_at,
            "harvest_status": catalogue.harvest_status,
            "total_resources": catalogue.total_resources,
        }
        for catalogue in catalogues
    ]
