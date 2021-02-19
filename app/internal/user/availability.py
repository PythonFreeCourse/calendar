from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Event, User
# from app.internal.utils import get_current_user


def disable(session: Session, user_id: int) -> bool:
    """this functions changes user status to disabled.
    returns:
    True if function worked properly
    False if it didn't."""
    future_events_user_owns = session.query(Event).filter(
        Event.start > datetime.now(), Event.owner_id == user_id).all()

    if future_events_user_owns:
        return False
    # if get_current_user(session) != user_id:
    #     return False
    """line above makes sure the user disabled is the current user logged
    & doesn't own any event.
    currently it doesn't uses get_current_user since logger is not
    merged yet, Ill add it when its impossible to mock a logged user."""

    user_disabled = session.query(User).get(user_id)
    user_disabled.disabled = True
    session.commit()
    return True


def enable(session: Session, user_id: int) -> bool:
    """this functions enables user- doesn't return anything.
    currently it doesn't uses get_current_user since logger is not
    merged yet, Ill add it when its impossible to mock a logged user."""
    # if get_current_user(session) != user_id:
    #    return False
    user_enabled = session.query(User).get(user_id)
    user_enabled.disabled = False
    session.commit()
    return True
