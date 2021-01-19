import datetime
from typing import List

from sqlalchemy.orm import Session

from app.database.models import Base, Event, UserEvent


def save(item, session: Session) -> bool:
    """Commits an instance to the db.
    source: app.database.database.Base"""

    if issubclass(item.__class__, Base):
        session.add(item)
        session.commit()
        return True
    return False


def get_user_events(session: Session, user_id: int) -> List[Event]:
    """Returns all events that the
    user participants in."""

    user_event = (
        session.query(UserEvent)
        .filter(UserEvent.user_id == user_id)
        .all()
    )
    return [ue.events for ue in user_event]


def sort_events_by_date(events: List[Event]) -> List[Event]:
    """Sorts the events by the start of the event."""

    events.sort(key=lambda event: event.start)
    return events


def filter_dates(events: List[Event], start: datetime, end: datetime) -> List[Event]:
    time_frame_events = [
        event for event in events
        if start <= event.start.date() <= end
    ]
    return time_frame_events


def create_model(session: Session, model_class, **kw):

    instance = model_class(**kw)
    session.add(instance)
    session.commit()
    return instance
