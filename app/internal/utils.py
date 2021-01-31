from sqlalchemy.orm import Session

from app.database.models import Base


def save(session: Session, item) -> bool:
    """Commits an instance to the db.
    source: app.database.models.Base"""

    if issubclass(item.__class__, Base):
        session.add(item)
        session.commit()
        return True
    return False


def create_model(session: Session, model_class, **kw):
    """Creates and saves a db model."""

    instance = model_class(**kw)
    save(session, instance)
    return instance


def delete_instance(session: Session, instance):
    """Deletes an instant from the db."""
    session.delete(instance)
    session.commit()
