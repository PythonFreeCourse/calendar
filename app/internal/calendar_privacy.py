from app.dependencies import get_db
from app.database.models import User
# TODO switch to using this when the user system is merged
# from app.internal.security.dependancies import (
#    current_user, CurrentUser)

from fastapi import Depends


# TODO add privacy as an attribute in current user
# in app.internal.security.dependancies
# when user system is merged
def can_show_calendar(
    requested_user_username: str,
    db: Depends(get_db),
    current_user: User
    # TODO to be added after user system is merged:
    # CurrentUser = Depends(current_user)
) -> bool:
    """Check whether current user can show the requested calendar"""
    requested_user = db.query(User).filter(
        User.username == requested_user_username
    ).first()
    privacy = current_user.privacy
    is_current_user = current_user.username == requested_user.username
    if privacy == 'Private' and is_current_user:
        return True

    elif privacy == 'Public':
        return True

    return False
