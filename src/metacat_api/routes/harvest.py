from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import ErrorResponse
from metacat_api.services.auth import is_admin
from metacat_api.services.harvest import harvest

router = APIRouter(prefix="/harvest", tags=["Harvest"])


@router.get(
    "/tasks",
    dependencies=[Depends(is_admin)],
)
async def get_tasks():
    from metacat_api.main import get_scheduler

    return [
        {
            "name": job.name,
            "id": job.id,
            "next_run_time": job.next_run_time,
        }
        for job in get_scheduler().get_jobs()
    ]


@router.post(
    "/{catalogue_id}",
    dependencies=[Depends(is_admin)],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"model": ErrorResponse},
    },
)
async def post_harvest(catalogue_id: str):
    try:
        await harvest(catalogue_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=str(e),
        ) from e
