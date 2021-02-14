from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Event, User, UserEvent
from internal.utils import get_current_user


def disable_user(session: Session, user_id: int) -> bool:
    """this functions changes user status to disabled.
    returns:
    True if function worked properly
    False if it didn't."""

    if get_current_user(session) != user_id:
        return False
    # line above makes sure the disabled user is the current user logged
    events_user_owns = list(session.query(Event).filter_by(owner_id=user_id))
    # if user owns any event, he won't be able to disable himself.
    if events_user_owns:
        return False

    # if user doesn't own any event,
    # we will disable him and remove the user from all of its future events.
    user_disabled = session.query(User).get(user_id)
    user_disabled.disabled = True
    future_events_for_user = session.query(UserEvent.id).join(
        Event, Event.id == UserEvent.event_id
        ).filter(
        UserEvent.user_id == user_id, Event.start > datetime.now()).all()
    # the query above finds events that user participates in the future.
    for event_connection in future_events_for_user:
        session.delete(event_connection)
    session.commit()
    return True
