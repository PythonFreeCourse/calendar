from typing import List

from sqlalchemy.orm import Session

from app.database.models import Event
from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events


def get_events_per_friend(
        session: Session,
        user_id: int,
        my_friend: str,
) -> List[Event]:
    """ My_friend is the name of a person that appears in the invite list of
    events. He is not necessarily a registered userץ The variable is used to
    show all events where we are both in the invitees list"""

    events_together = []
    sorted_events = sort_by_date(get_all_user_events(session, user_id))
    for event in sorted_events:
        if my_friend in event.invitees.split(','):
            events_together.append(event)
    return events_together
