from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.database.models import Event, UserEvent


def get_upcoming_events(session: Session, user_id: int) -> List[Event]:
    upcoming_events = (
        session.query(Event).join(UserEvent)
        .filter(UserEvent.user_id == user_id)
        .filter(Event.start >= datetime.now())
        .order_by(Event.start)
        )
    return upcoming_events
