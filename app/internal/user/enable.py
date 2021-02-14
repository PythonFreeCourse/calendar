from sqlalchemy.orm import Session

from app.database.models import User
# from app.internal.utils import get_current_user


def enable_user(session: Session, user_id: int) -> bool:
    """this functions enables user- doesn't return anything.
    currently it doesn't uses get_current_user since logger is not
    merged yet, Ill add it when its impossible to mock a logged user."""
    # if get_current_user(session) != user_id:
    #    return False
    user_enabled = session.query(User).get(user_id)
    user_enabled.disabled = False
    session.commit()
    return True
