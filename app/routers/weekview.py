from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.database.database import get_db
from app.database.models import Event
from app.dependencies import TEMPLATES_PATH
from app.routers.dayview import dayview, DivAttributes


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
                                session='') -> templates.TemplateResponse:
    view = 'week'
    template = await dayview(request=req,
                             date=day.strftime('%Y-%m-%d'),
                             #db_session=session,
                             view=view)
    print(template)
    return template


@router.get('/week/{sunday}')
async def weekview(request: Request, sunday: str, db_session=Depends(get_db)):
    sunday = datetime.strptime(sunday, '%Y-%m-%d')
    week_days = get_week_dates(sunday)
    '''week = [(day, await get_day_view_template(
        req=request, day=day, session=db_session)
        ) for day in week_days]'''
    start = datetime(year=2021, month=2, day=1, hour=13, minute=13)
    end = datetime(year=2021, month=2, day=1, hour=15, minute=46)
    events = [Event(title='test2', content='test',
                 start=start, end=end, owner_id=1, color='pink')]
    week = [(day, await get_day_view_template(
        req=request, day=day)
        ) for day in week_days]
    day = sunday
    events_n_attrs = [(event, DivAttributes(event, day)) for event in events]
    return templates.TemplateResponse("weekview.html", {
        "request": request,
        "week": week,
        "weekly_events": events_n_attrs
        })
