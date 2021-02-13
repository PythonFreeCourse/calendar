from typing import Any, Dict

from sqlalchemy.orm import Session

from app.database.models import Base, User
from app.routers.profile import get_placeholder_user


def save(session: Session, instance: Base) -> bool:
    """Commits an instance to the db.
    source: app.database.models.Base"""

    if issubclass(instance.__class__, Base):
        session.add(instance)
        session.commit()
        return True
    return False


def create_model(session: Session, model_class: Base,
                 **kw: Dict[str, Any]) -> Base:
    """Creates and saves a db model."""

    instance = model_class(**kw)
    save(session, instance)
    return instance


def delete_instance(session: Session, instance: Base) -> None:
    """Deletes an instant from the db."""
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
