from typing import List

from sqlalchemy.orm import Session

from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events


def get_events_per_friend(
        session: Session,
        user_id: int,
        my_friend: str,
) -> List:

    events_together = []
    sorted_events = sort_by_date(get_all_user_events(session, user_id))
    for event in sorted_events:
        if my_friend in event.invitees.split(','):
            events_together.append(event)
    return events_together
