import datetime
from http import HTTPStatus

from app.dependencies import templates
from app.routers import calendar_grid as cg
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)

ADD_DAYS_ON_SCROLL: int = 42


@router.get("/")
async def calendar(request: Request) -> Response:
    day = cg.create_day(datetime.date.today())
    return templates.TemplateResponse(
        "calendar/calendar.html",
        {
            "request": request,
            "day": day,
            "week_days": cg.Week.DAYS_OF_THE_WEEK,
            "weeks_block": cg.get_month_block(day)
        }
    )


@ router.get("/{date}")
async def update_calendar(request: Request, date: str) -> HTMLResponse:
    last_day = cg.Day.convert_str_to_date(date)
    next_weeks = cg.create_weeks(cg.get_n_days(last_day, ADD_DAYS_ON_SCROLL))
    template = templates.get_template('calendar/add_week.html')
    content = template.render(weeks_block=next_weeks)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)
