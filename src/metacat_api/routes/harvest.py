from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import ErrorResponse, Task
from metacat_api.services.auth import is_api_key_valid
from metacat_api.services.harvest import harvest, harvest_all
from metacat_api.services.schedule import get_scheduled_tasks, pause_scheduled_job, resume_scheduled_job

router = APIRouter(prefix="/harvest", tags=["Harvest"])


@router.get(
    "/tasks",
    dependencies=[Depends(is_api_key_valid)],
    summary="Scheduled tasks information",
)
async def get_tasks() -> list[Task]:
    return get_scheduled_tasks()


@router.post(
    "/tasks/{task_id}/pause",
    dependencies=[Depends(is_api_key_valid)],
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Pause a scheduled task",
)
async def pause_tasks(task_id: str) -> None:
    pause_scheduled_job(task_id)


@router.post(
    "/tasks/{task_id}/resume",
    dependencies=[Depends(is_api_key_valid)],
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resume a scheduled task",
)
async def resume_tasks(task_id: str) -> None:
    resume_scheduled_job(task_id)


@router.post(
    "/{catalogue_id}",
    dependencies=[Depends(is_api_key_valid)],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_408_REQUEST_TIMEOUT: {"model": ErrorResponse},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Harvest a specific catalogue or all",
)
async def post_harvest(catalogue_id: str) -> None:
    try:
        if catalogue_id == "all":
            await harvest_all()
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
