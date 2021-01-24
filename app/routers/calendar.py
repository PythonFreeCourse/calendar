import datetime

from app.dependencies import templates
from app.routers import calendar_grid as cg
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def calendar(request: Request):
    day = cg.create_day(datetime.date.today())
    return templates.TemplateResponse(
        "calendar/calendar.html",
        {
            "request": request,
            "calendar": {
                'day': day,
                'week_days': cg.Week.DAYS_OF_THE_WEEK,
                'month_block': cg.get_month_block(day)
            }
        }
    )


@ router.get("/{date}")
async def update_calendar(request: Request, date: str):
    last_day = cg.Day.convert_str_to_date(date)
    next_week = cg.Week(cg.get_n_days(last_day, 7))
    template = templates.get_template('calendar/add_week.html')
    content = template.render(week=next_week.days)
    return HTMLResponse(content=content, status_code=200)
