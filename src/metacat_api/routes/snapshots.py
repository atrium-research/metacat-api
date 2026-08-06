from fastapi import APIRouter, HTTPException, status

from metacat_api.datasources.json_store import datasource
from metacat_api.models import ErrorResponse, Snapshot

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


@router.get("", summary="List snapshots")
def list_snapshots() -> list[Snapshot]:
    return sorted(datasource.snapshots(), key=lambda snapshot: snapshot.taken_at)


@router.get(
    "/latest",
    responses=_NOT_FOUND,
    summary="Current snapshot metadata",
)
def latest_snapshot() -> Snapshot:
    snapshots = datasource.snapshots()
    if not snapshots:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No snapshot available")
    return max(snapshots, key=lambda snapshot: snapshot.taken_at)
