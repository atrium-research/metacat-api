from fastapi import Security, status
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyQuery

from metacat_api.config import settings

_query_scheme = APIKeyQuery(name="metacat_api_key")


def is_admin(api_key: str = Security(_query_scheme)):
    if api_key and settings.admin_password and api_key.encode("utf-8") == settings.admin_password.encode("utf-8"):
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")
