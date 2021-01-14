from sqlalchemy.exc import SQLAlchemyError

from app.config import session
from app.database.models import User
from app.utils.utils import save


def create_user(username, password, email) -> User:
    """Creates and saves a new user."""

    user = User(
        username=username,
        password=password,
        email=email,
    )
    save(user)
    return user


def get_users(**param):
    """Returns all users filter by param."""

    try:
        users = list(session.query(User).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return users


def does_user_exist(*_, user_id=None, username=None, email=None):
    """Returns if user exists. function can
    receive one of the there parameters"""

    if user_id:
        return len(get_users(id=user_id)) == 1
    if username:
        return len(get_users(username=username)) == 1
    if email:
        return len(get_users(email=email)) == 1
    return False
