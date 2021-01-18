from datetime import date, timedelta
from typing import List, Optional

from app.database.models import Event
from app.database.database import SessionLocal
import arrow
from sqlalchemy.exc import SQLAlchemyError


def get_events_per_dates(
        session: SessionLocal,
        user_id: int,
        start: Optional[date],
        end: Optional[date]
        ) -> List[Event]:
    """Read from the db. Return a list of all the user events between
    the relevant dates."""
    if start > end:
        return []
    try:
        events = (
            session.query(Event).filter(Event.owner_id == user_id)
            .filter(Event.start.between(start, end + timedelta(days=1)))
            .order_by(Event.start).all()
            )
    except SQLAlchemyError:
        return []
    else:
        return events


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
