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


@router.post("/{date}")
async def update_calendar(request: Request, date: str):
    last_day = cg.Day.convert_str_to_date(date)
    next_week = cg.Week(cg.get_n_days(last_day, 7))
    next_week.display_week()

    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "next_week": next_week
        }
    )
