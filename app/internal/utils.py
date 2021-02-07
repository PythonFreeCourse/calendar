from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import Base, User


def save(item, session: Session) -> bool:
    """Commits an instance to the db.
    source: app.database.database.Base"""

    if issubclass(item.__class__, Base):
        session.add(item)
        session.commit()
        return True
    return False


def create_model(session: Session, model_class, **kw):
    """Creates and saves a db model."""

    instance = model_class(**kw)
    save(instance, session)
    return instance


def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.query(User).filter_by(id=user_id).first()
