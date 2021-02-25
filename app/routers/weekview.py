from datetime import datetime, timedelta
from itertools import accumulate
from typing import Iterator, NamedTuple, Tuple

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session

from app.database.models import Event, User
from app.dependencies import TEMPLATES_PATH, get_db
from app.internal.security.dependencies import current_user
from app.routers.dayview import (
    CurrentTimeAttributes,
    EventsAttributes,
    dayview,
    get_all_day_events,
    get_events_and_attributes,
)

templates = Jinja2Templates(directory=TEMPLATES_PATH)


router = APIRouter()


class DayEventsAndAttrs(NamedTuple):
    day: datetime
    template: Jinja2Templates.TemplateResponse
    events_and_attrs: Tuple[Event, EventsAttributes]
    current_time_and_attrs: CurrentTimeAttributes
    all_day_events: Event


def get_week_dates(first_day: datetime) -> Iterator[datetime]:
    rest_of_days = [timedelta(days=1) for _ in range(6)]
    rest_of_days.insert(0, first_day)
    return accumulate(rest_of_days)


async def get_day_events_and_attributes(
    request: Request,
    day: datetime,
    session: Session,
    user: User,
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
    current_time_and_attrs = CurrentTimeAttributes(date=day)
    all_day_events = get_all_day_events(
        day=day,
        session=session,
        user_id=user.user_id,
    )
    return DayEventsAndAttrs(
        day,
        template,
        events_and_attrs,
        current_time_and_attrs,
        all_day_events,
    )


@router.get("/week/{first_day}")
async def weekview(
    request: Request,
    first_day: str,
    session=Depends(get_db),
    user: User = Depends(current_user),
):
    first_day = datetime.strptime(first_day, "%Y-%m-%d")
    week_days = get_week_dates(first_day)
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
