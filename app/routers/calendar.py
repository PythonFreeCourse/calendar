from http import HTTPStatus

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from app.dependencies import get_db, templates
from app.internal import load_hebrew_view
from app.routers import calendar_grid as cg

router = APIRouter(
    prefix="/calendar/month",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)

ADD_DAYS_ON_SCROLL: int = 42


@router.get("/")
async def calendar(request: Request, db_session=Depends(get_db)) -> Response:
    user_local_time = cg.Day.get_user_local_time()
    day = cg.create_day(user_local_time)
    hebrew_obj = load_hebrew_view.get_hebrew_dates(db_session)
    return templates.TemplateResponse(
        "calendar_monthly_view.html",
        {
            "request": request,
            "day": day,
            "week_days": cg.Week.DAYS_OF_THE_WEEK,
            "weeks_block": cg.get_month_block(day),
            "hebrewView": hebrew_obj

        }
    )


@router.get("/{date}")
async def update_calendar(request: Request, date: str) -> HTMLResponse:
    last_day = cg.Day.convert_str_to_date(date)
    next_weeks = cg.create_weeks(cg.get_n_days(last_day, ADD_DAYS_ON_SCROLL))
    template = templates.get_template(
        'partials/calendar/monthly_view/add_week.html')
    content = template.render(weeks_block=next_weeks)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)
