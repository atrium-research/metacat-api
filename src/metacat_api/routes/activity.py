from fastapi import APIRouter

from metacat_api.datasources import datasource_dep

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get(
    "",
    summary="Latest harvest activity per catalogue for the Overview panel",
)
def activity(ds: datasource_dep) -> list[dict]:
    catalogues = sorted(ds.catalogues(), key=lambda catalogue: catalogue.last_harvest_at, reverse=True)
    return [
        {
            "catalogue_id": catalogue.id,
            "name": catalogue.name,
            "last_harvest_at": catalogue.last_harvest_at,
            "harvest_status": catalogue.harvest_status,
            "total_resources": catalogue.total_resources,
        }
        for catalogue in catalogues
    ]
