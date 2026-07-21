from fastapi import APIRouter, HTTPException

from metacat_api.datasources import datasource_dep
from metacat_api.models.common import ErrorResponse
from metacat_api.models.snapshot import Snapshot

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


@router.get("", summary="List snapshots")
def list_snapshots(ds: datasource_dep) -> list[Snapshot]:
    return sorted(ds.snapshots(), key=lambda snapshot: snapshot.taken_at)


@router.get(
    "/latest",
    responses={404: {"model": ErrorResponse}},
    summary="Current snapshot metadata",
)
def latest_snapshot(ds: datasource_dep) -> Snapshot:
    snapshots = ds.snapshots()
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshot available")
    return max(snapshots, key=lambda snapshot: snapshot.taken_at)
