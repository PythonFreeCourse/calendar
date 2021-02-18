import datetime
from datetime import date, timedelta
from typing import Iterator, List, Optional, Union

import arrow
from sqlalchemy.orm import Session

from app.database.models import Event
from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events


def get_events_per_dates(
        session: Session,
        user_id: int,
        start: Optional[date],
        end: Optional[date]
) -> Union[Iterator[Event], list]:
    """Read from the db. Return a list of all
    the user events between the relevant dates."""

    if start > end:
        return []

    return (
        filter_dates(
            sort_by_date(
                get_all_user_events(session, user_id)
            ),
            start,
            end,
        )
    )


def build_arrow_delta_granularity(diff: timedelta) -> List[str]:
    """Builds the granularity for the arrow module string"""
    granularity = []
    if diff.days > 0:
        granularity.append("day")
    hours, remainder = divmod(diff.seconds, 60 * 60)
    if hours > 0:
        granularity.append("hour")
    minutes, _ = divmod(remainder, 60)
    if minutes > 0:
        granularity.append("minute")
    return granularity


def get_time_delta_string(start: date, end: date) -> str:
    """Builds a string of the event's duration- days, hours and minutes."""
    arrow_start = arrow.get(start)
    arrow_end = arrow.get(end)
    diff = end - start
    granularity = build_arrow_delta_granularity(diff)
    duration_string = arrow_end.humanize(
        arrow_start, only_distance=True, granularity=granularity
    )
    return duration_string


def filter_dates(
        events: List[Event],
        start: Union[None, date] = None,
        end: Union[None, date] = None,
) -> Iterator[Event]:
    """Returns all events in a time frame.

    if "start_date" or "end_date" are None,
    it will ignore that parameter when filtering.

    for example:
    if start_date = None and end_date = datetime.now().date,
    then the function will return all events that ends before end_date.
    """
    start = start or datetime.date.min
    end = end or datetime.date.max

    for event in events:
        if start <= event.start.date() <= end:
            yield event


def get_events_in_time_frame(
        start_date: Union[date, None],
        end_date: Union[date, None],
        user_id: int, db: Session
) -> Iterator[Event]:
    """Yields all user's events in a time frame."""
    events = get_all_user_events(db, user_id)
    yield from filter_dates(events, start_date, end_date)
