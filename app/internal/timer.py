from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from app.database.models import Event, UserEvent


def get_next_user_event(session: Session, user_id: int) -> List[Event]:
    next_user_event = (
        session.query(Event).join(UserEvent)
        .filter(UserEvent.user_id == user_id)
        .filter(Event.start >= datetime.now())
        .order_by(Event.start)
        )
    return next_user_event[0]


def get_next_user_event_start_time(
    session: Session,
    user_id: int
) -> Dict[str, Optional[str]]:
    next_event = get_next_user_event(session, user_id)
    timer_to_next_event = None
    if next_event is not None:
        timer_to_next_event = next_event.start.strftime("%Y-%m-%d %H:%M")
    return {"timer": timer_to_next_event}
