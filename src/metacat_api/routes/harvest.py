from fastapi import APIRouter

router = APIRouter(prefix="/harvest", tags=["Harvest"])


@router.get("/tasks")
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
