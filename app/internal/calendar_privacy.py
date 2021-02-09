from app.database.database import get_db
from app.database.models import User
# from app.internal.security.dependancies import (
#    current_user, CurrentUser)

from fastapi import Depends


# TODO add privacy as an attribute in current user
# in app.internal.security.dependancies
def can_show_calendar(
    requested_user_username: str,
    db: Depends(get_db),
    current_user: User
):
    # to be added after user system is merged:
    # CurrentUser = Depends(current_user)):
    """Check whether current user can show the requested calendar"""
    requested_user = db.query(User).filter(
        User.username == requested_user_username
    ).first()
    privacy = current_user.privacy
    if privacy == 'Private' and (
        current_user.username == requested_user.username
    ):
        return True

    elif privacy == 'Public':
        return True

    return
