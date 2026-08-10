import logging

from fastapi import Security, status
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery

from metacat_api.config import settings

_query_scheme = APIKeyQuery(name="api_key", auto_error=False)
_header_scheme = APIKeyHeader(name="x-api-key", auto_error=False)

logger = logging.getLogger(__name__)


def is_api_key_valid(
    api_key_query: str = Security(_query_scheme),
    api_key_header: str = Security(_header_scheme),
):
    api_key = api_key_query or api_key_header
    if (
        api_key
        and settings.api_keys_bytes
        and api_key.encode("utf-8") in [k.get_secret_value() for k in settings.api_keys_bytes]
    ):
        return
    logger.warning(
        "Forbidden authentication",
        extra={
            "extra_fields": {
                "api_key_query": api_key_query,
                "api_key_header": api_key_header,
            }
        },
    )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")
