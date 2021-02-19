from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.database.models import Base, User


def save(session: Session, instance: Base) -> bool:
    """Commits an instance to the db.
    source: app.database.models.Base"""
    if issubclass(instance.__class__, Base):
        session.add(instance)
        session.commit()
        return True
    return False


def create_model(session: Session, model_class: Base, **kwargs: Any) -> Base:
    """Creates and saves a db model."""
    instance = model_class(**kwargs)
    save(session, instance)
    return instance


def delete_instance(session: Session, instance: Base) -> None:
    """Deletes an instance from the db."""
    session.delete(instance)
    session.commit()


def get_current_user(session: Session) -> User:
    """Mock function for current user information retrival."""
    # Code revision required after user login feature is added
    new_user = get_placeholder_user()
    user = session.query(User).first()
    if not user:
        save(session, new_user)
        user = session.query(User).first()

    return user


def get_available_users(session: Session) -> List[User]:
    """this function return all availible users."""
    return session.query(User).filter(not User.disabled).all()


def get_user(session: Session, user_id: int) -> Optional[User]:
    """Returns User instance for `user_id` if exists, None otherwise.

    Args:
        session (Session): DB session.
        user_id (int): ID of user to return.

    Returns:
        (User | None): User instance for `user_id` if exists, None otherwise.
    """
    return session.query(User).filter_by(id=user_id).first()


def get_placeholder_user() -> User:
    """Creates a mock user.

    This is a temporarily function which should be removed when a
    real system is created.

    Returns:
        A User object.
    """
    return User(
        username='new_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name',
        language_id=1,
        telegram_id='',
    )
