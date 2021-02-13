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
        events: List[Event], start: Optional[date],
        end: Optional[date]) -> Iterator[Event]:
    """filter events by a time frame."""

    yield from (
        event for event in events
        if start <= event.start.date() <= end
    )
