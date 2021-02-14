from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Event
from internal.utils import get_current_user


def disable_user(session: Session, user_id: int) -> bool:
    """this functions changes user status to disabled.
    returns:
    True if function worked properly
    False if it didn't."""

    if get_current_user(session) != user_id:
        return False
    # line above makes sure the disabled user is the current user logged
    future_events_user_owns = session.query(Event).filter(
        Event.start > datetime.now(), Event.owner_id == user_id).all()
    # if user owns any event, he won't be able to disable himself.
    if future_events_user_owns:
        return False

    session.commit()
    return True
