from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.database.models import Event, UserEvent
from operator import attrgetter


def get_all_user_events(session: Session, user_id: int) -> List[Event]:
    return (
        session.query(Event).join(UserEvent)
        .filter(UserEvent.user_id == user_id).all()
    )


def sort_by_date(events: List[Event]) -> List[Event]:
    temp = events.copy()
    return sorted(temp, key=attrgetter('start'))


def filter_by_now(events: List[Event]) -> List[Event]:
    upcoming_events = []
    for event in events:
        if event.start >= datetime.now():
            upcoming_events.append(event)
    return upcoming_events


def get_upcoming_events(session: Session, user_id: int) -> List:
    return filter_by_now(sort_by_date(get_all_user_events(session, user_id)))
