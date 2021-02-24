import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, UserEvent


@pytest.fixture
def association(event: Event, session: Session) -> UserEvent:
    return (
        session.query(UserEvent)
        .filter(UserEvent.event_id == event.id)
    ).first()
