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
        events: List[Event], start: Optional[date],
        end: Optional[date]) -> Iterator[Event]:
    """filter events by a time frame."""

    yield from (
        event for event in events
        if start <= event.start.date() <= end
    )
