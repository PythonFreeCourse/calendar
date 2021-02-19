from datetime import datetime, timedelta
from itertools import accumulate
from typing import Iterator, NamedTuple, Tuple

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session

from app.database.models import Event
from app.dependencies import get_db, TEMPLATES_PATH
from app.internal.security.dependancies import current_user, schema
from app.routers.dayview import (
    DivAttributes,
    dayview,
    get_events_and_attributes,
)

templates = Jinja2Templates(directory=TEMPLATES_PATH)

router = APIRouter()


class DayEventsAndAttrs(NamedTuple):
    day: datetime
    template: Jinja2Templates.TemplateResponse
    events_and_attrs: Tuple[Event, DivAttributes]


def get_week_dates(firstday: datetime) -> Iterator[datetime]:
    rest_of_days = [timedelta(days=1) for _ in range(6)]
    rest_of_days.insert(0, firstday)
    return accumulate(rest_of_days)


async def get_day_events_and_attributes(
    request: Request,
    day: datetime,
    session: Session,
    user: schema.CurrentUser,
) -> DayEventsAndAttrs:
    template = await dayview(
        request=request,
        date=day.strftime("%Y-%m-%d"),
        view="week",
        session=session,
        user=user,
    )
    events_and_attrs = get_events_and_attributes(
        day=day,
        session=session,
        user_id=user.user_id,
    )
    return DayEventsAndAttrs(day, template, list(events_and_attrs))


@router.get("/week/{firstday}")
async def weekview(
    request: Request,
    firstday: str,
    session: Session = Depends(get_db),
    user: schema.CurrentUser = Depends(current_user),
):
    firstday = datetime.strptime(firstday, "%Y-%m-%d")
    week_days = get_week_dates(firstday)
    week = [
        await get_day_events_and_attributes(request, day, session, user)
        for day in week_days
    ]
    return templates.TemplateResponse(
        "weekview.html",
        {
            "request": request,
            "week": week,
        },
    )
