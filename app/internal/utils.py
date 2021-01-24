from sqlalchemy.orm import Session

from app.database.models import Base


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
