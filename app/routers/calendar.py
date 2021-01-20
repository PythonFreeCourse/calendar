import datetime

from app.dependencies import templates
from app.routers import calendar_grid as cg
from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def calendar(request: Request):
    today = cg.Day(datetime.date.today())
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "calendar": {
                'day': today,
                'week_days': cg.Week.DAYS_OF_THE_WEEK,
                'month_block': cg.get_month_block(
                    datetime.date(today.date.year, today.date.month, 1)
                )
            }
        }
    )
