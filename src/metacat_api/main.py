from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from metacat_api import __version__
from metacat_api.config import settings
from metacat_api.logging_setup import setup_logging
from metacat_api.models.common import ErrorResponse
from metacat_api.routes import (
    activity,
    catalogues,
    facets,
    harvest,
    mappings,
    snapshots,
    system,
    vocabularies,
)
from metacat_api.services.schedule import get_scheduler

DESCRIPTION = (
    "REST serving layer for the MetaCat dashboard. MetaCat catalogues the four major "
    "SSH European catalogues (ARIADNE Portal, CLARIN VLO, GoTriple, SSH Open Marketplace), "
    "their facets, controlled vocabularies and cross-mappings. The smallest queryable unit "
    "is always a catalogue, on a facet, at a moment in time. "
    "Source: https://github.com/atrium-research/metacat-api"
)

STATUS_CODES = {
    400: "bad_request",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    500: "internal_error",
}

_V1_ROUTERS = (
    catalogues.router,
    facets.router,
    vocabularies.router,
    mappings.router,
    snapshots.router,
    activity.router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    get_scheduler().shutdown()


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="MetaCat API",
        description=DESCRIPTION,
        version=__version__,
        contact={"name": "Foxcub", "email": "julien.homo@foxcub.fr"},
        license_info={"name": "Apache-2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
        code = STATUS_CODES.get(exc.status_code, "error")
        body = ErrorResponse(detail=str(exc.detail), code=code)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
        body = ErrorResponse(detail="Request validation failed", code="validation_error")
        return JSONResponse(status_code=422, content=body.model_dump())

    for router in _V1_ROUTERS:
        app.include_router(router, prefix="/v1")
    app.include_router(system.router)
    app.include_router(harvest.router)

    return app


app = create_app()
