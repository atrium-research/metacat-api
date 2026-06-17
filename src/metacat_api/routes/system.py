from fastapi import APIRouter

from metacat_api import __version__

router = APIRouter(tags=["system"])


@router.get("/health", summary="Liveness probe")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version", summary="Application name and version")
def version() -> dict:
    return {"name": "MetaCat API", "version": __version__}
