from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.database.database import get_db
from app.dependencies import TEMPLATES_PATH
from app.routers.dayview import dayview


templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


def get_week_dates(sunday: datetime) -> List[datetime]:
    week_dates = [sunday]
    a_day = timedelta(hours=24)
    next_day = sunday + a_day
    for _ in range(6):
        week_dates.append(next_day)
        next_day += a_day
    return week_dates


async def get_day_view_template(req: Request,
                                day: datetime,
                                session) -> templates.TemplateResponse:
    view = 'week'
    if day.strftime('%A') == 'Sunday':
        view = 'sunday'
    template = await dayview(request=req,
                             date=day.strftime('%Y-%m-%d'),
                             db_session=session,
                             view=view)
    return template


@router.get('/week/{sunday}')
async def weekview(request: Request, sunday: str, db_session=Depends(get_db)):
    sunday = datetime.strptime(sunday, '%Y-%m-%d')
    week_days = get_week_dates(sunday)
    week = [(day, await get_day_view_template(
        req=request, day=day, session=db_session)
        ) for day in week_days]
    return templates.TemplateResponse("weekview.html", {
        "request": request,
        "week": week
        })
