from app.database.models import User, UserSettings
from sqlalchemy.orm.session import Session
from typing import List, Optional, Tuple


def get_cursor_settings(
    session: Session,
    user_id: int,
) -> Tuple[Optional[List[str]], Optional[int], Optional[str], Optional[int]]:
    """Retrieves cursor settings from the database.

    Args:
        session (Session): the database.
        user_id (int, optional): the users' id.

    Returns:
        Tuple[str, Optional[List[str]], Optional[int],
        str, Optional[str], Optional[int]]: the cursor settings.
    """
    primary_cursor, secondary_cursor = None, None
    cursor_settings = (
        session.query(UserSettings).filter_by(user_id=user_id).first()
    )
    if cursor_settings:
        primary_cursor = cursor_settings.primary_cursor
        secondary_cursor = cursor_settings.secondary_cursor

    return primary_cursor, secondary_cursor


def save_cursor_settings(
    session: Session,
    user: User,
    cursor_choices: List[str],
):
    """Saves cursor choices in the db.

    Args:
        session (Session): the database.
        user (User): current user.
        cursor_choices (List[str]): primary and secondary cursors.
    """
    cursor_settings = (
        session.query(UserSettings).filter_by(user_id=user.user_id).first()
    )
    if cursor_settings:
        session.query(UserSettings).filter_by(
            user_id=cursor_settings.user_id,
        ).update(cursor_choices)
        session.commit()
    else:
        cursor_settings = UserSettings(user_id=user.user_id, **cursor_choices)
        session.add(cursor_settings)
        session.commit()
