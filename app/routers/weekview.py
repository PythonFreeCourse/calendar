from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session

from app.database.database import get_db
from app.database.models import User
from app.dependencies import TEMPLATES_PATH
from app.routers.dayview import dayview, get_events_and_attributes


templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


def get_week_dates(firstday: datetime) -> List[datetime]:
    week_dates = [firstday]
    a_day = timedelta(hours=24)
    next_day = firstday + a_day
    for _ in range(6):
        week_dates.append(next_day)
        next_day += a_day
    return week_dates


async def get_week_events_and_attributes(
        request: Request, day: datetime, session: Session, user: User
      ):
    template = await dayview(
        request=request,
        date=day.strftime('%Y-%m-%d'),
        view='week',
        db_session=session
    )
    events_and_attrs = get_events_and_attributes(
            day=day, session=session, user_id=user.id)
    return (day, template, events_and_attrs)


@router.get('/week/{firstday}')
async def weekview(
          request: Request, firstday: str, db_session=Depends(get_db)
      ):
    user = db_session.query(User).filter_by(username='test_username').first()
    firstday = datetime.strptime(firstday, '%Y-%m-%d')
    week_days = get_week_dates(firstday)
    week = [await get_week_events_and_attributes(
                request=request, day=day, session=db_session, user=user
            ) for day in week_days]
    return templates.TemplateResponse("weekview.html", {
        "request": request,
        "week": week,
        })
