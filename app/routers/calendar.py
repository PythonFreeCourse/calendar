from http import HTTPStatus

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from app.dependencies import get_db, templates
from app.routers import calendar_grid


router = APIRouter(
    prefix="/calendar/month",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
    include_in_schema=False
)


@router.get("/")
async def calendar(request: Request, db_session=Depends(get_db)) -> Response:
    user_local_time = calendar_grid.Day.get_user_local_time()
    day = calendar_grid.create_day(user_local_time)
    return templates.TemplateResponse(
        "calendar_monthly_view.html",
        {
            "request": request,
            "day": day,
            "week_days": calendar_grid.Week.DAYS_OF_THE_WEEK,
            "weeks_block": calendar_grid.get_month_block(day),
        }
    )


@router.get("/add/{date}")
async def update_calendar(
    request: Request, date: str, days: int
) -> HTMLResponse:
    last_day = calendar_grid.Day.convert_str_to_date(date)
    next_weeks = calendar_grid.create_weeks(
        calendar_grid.get_n_days(last_day, days)
    )
    template = templates.get_template(
        'partials/calendar/monthly_view/add_week.html')
    content = template.render(weeks_block=next_weeks)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)
