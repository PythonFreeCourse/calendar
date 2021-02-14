import datetime
from datetime import date
from typing import Iterator, List, Optional, Union

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
