from app.dependencies import templates
from app.routers import calendar_grid as cg
from fastapi import APIRouter, Request
from starlette.responses import Response

router = APIRouter(
    prefix="/features",
    tags=["features"],
    responses={404: {"description": "Not found"}}
)


@router.get("/")
async def calendar(request: Request) -> Response:
    user_local_time = cg.Day.get_user_local_time()
    day = cg.create_day(user_local_time)
    return templates.TemplateResponse(
        "features.html",
        {
            "request": request,
            "day": day
        }
    )
