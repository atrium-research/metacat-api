from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from metacat_api.config import get_version

router = APIRouter(tags=["System"])


class Health(BaseModel):
    status: Literal["ok", "error"]


@router.get("/health", summary="Liveness probe")
def health() -> Health:
    return Health(status="ok")


class Version(BaseModel):
    name: str
    version: str


@router.get("/version", summary="Application name and version")
def version() -> Version:
    return Version(name="MetaCat API", version=get_version())
