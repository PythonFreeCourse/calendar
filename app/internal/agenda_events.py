from datetime import date, datetime, timedelta
from typing import Optional

from app.database.models import Event
from app.database.database import SessionLocal

from sqlalchemy.exc import SQLAlchemyError


def get_events_per_dates(session: SessionLocal, user_id: int, start: Optional[date], end: Optional[date]) -> list:
    """Read function from the db. Return a list of all the user events between
    the relevant dates."""
    if start > end:
        return []
    try:
        events = (
            session.query(Event).filter(Event.owner_id == user_id)
            .filter((Event.start >= start) & (Event.start <= end + timedelta(days=1)))
            .order_by(Event.start).all()
            )
    except SQLAlchemyError:
        return []
    else:
        return events


def calc_dates_range_for_agenda(start: Optional[date], end: Optional[date], days: Optional[int]) -> (date, date):
    """Create start and end dates eccording to the parameters in the page."""
    if days is not None:
        start = date.today()
        end = start + timedelta(days=days)
    elif start is None or end is None:
        start = date.today()
        end = date.today()
    return start, end


def get_time_delta_string(start_date: date, end_date: date) -> str:
    """Rerurn time delta as string- by days, hours or minutes."""
    total_minutes = (end_date - start_date).total_seconds() / 60
    days = int(total_minutes / (24 * 60 ))
    hours = int((total_minutes - (days * 24 * 60)) / 60)
    minutes = int(total_minutes - (days * 24 * 60 + hours * 60))
    if days > 0:
        if hours == 0 and minutes == 0:
            return f'{days} days'
        if hours > 0 and minutes == 0:
            return f'{days} days, {hours} hours'
        return f'{days} days, {hours}:{minutes} hours'
    if hours > 0:
        if minutes > 0:
            return f'{hours}:{minutes} hours'
        return f'{hours} hours'
    return f'{minutes} minutes'