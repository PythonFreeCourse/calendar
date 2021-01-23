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
    day = cg.create_day(datetime.date.today())
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "calendar": {
                'day': day,
                'week_days': cg.Week.DAYS_OF_THE_WEEK,
                'month_block': cg.get_month_block(day)
            }
        }
    )


@router.post("/nextweek")
async def calendar_next(request: Request):
    last_day = cg.LAST_SHOWED_DAY
    next_week = cg.get_n_days(last_day, cg.Week.WEEK_DAYS)
    cg.LAST_SHOWED_DAY = next_week[-1].date

    return templates.TemplateResponse(
        "add_week.html",
        {
            "request": request,
            "next_week": next_week
        }
    )
