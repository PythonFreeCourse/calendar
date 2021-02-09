from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events
from sqlalchemy.orm import Session
from app.database.models import Event


def get_next_user_event(session: Session, user_id: int) -> Event:
    events_as_list = list(sort_by_date(get_all_user_events(session, user_id)))
    next_event = None
    if len(events_as_list) > 0:
        next_event = events_as_list[0]
    return next_event


def get_next_user_event_start_time(session: Session, user_id: int):
    next_event = get_next_user_event(session, user_id)
    if next_event is None:
        timer_to_next_event = None
    else:
        timer_to_next_event = next_event.start.strftime("%Y-%m-%d %H:%M")
    return {"timer": timer_to_next_event}
