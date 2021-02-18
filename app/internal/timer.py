from typing import Dict, Optional

from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events
from sqlalchemy.orm import Session
from app.database.models import Event


def get_next_user_event(session: Session, user_id: int) -> Optional[Event]:
    events = list(sort_by_date(get_all_user_events(session, user_id)))
    if events:
        return events[0]


def get_next_user_event_start_time(
    session: Session,
    user_id: int
) -> Dict[str, Optional[str]]:
    next_event = get_next_user_event(session, user_id)
    timer_to_next_event = None
    if next_event is not None:
        timer_to_next_event = next_event.start.strftime("%Y-%m-%d %H:%M")
    return {"timer": timer_to_next_event}
