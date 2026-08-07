from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import ErrorResponse, Task
from metacat_api.services.auth import is_api_key_valid
from metacat_api.services.harvest import harvest, harvest_all_async

router = APIRouter(prefix="/harvest", tags=["Harvest"])


@router.get(
    "/tasks",
    dependencies=[Depends(is_api_key_valid)],
)
async def get_tasks():
    from metacat_api.main import get_scheduler

    return [
        Task.model_validate(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            },
            extra="forbid",
        )
        for job in get_scheduler().get_jobs()
    ]


@router.post(
    "/{catalogue_id}",
    dependencies=[Depends(is_api_key_valid)],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"model": ErrorResponse},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def post_harvest(catalogue_id: str) -> None:
    try:
        if catalogue_id == "all":
            await harvest_all_async()
        else:
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
