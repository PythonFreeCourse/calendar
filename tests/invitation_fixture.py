from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, Invitation, User
from tests.utils import create_model, delete_instance


@pytest.fixture
def invitation(event: Event, user: User, session: Session) -> Event:
    invitation = create_model(
        session, Invitation,
        creation=datetime.now(),
        recipient=user,
        event=event,
        event_id=event.id,
        recipient_id=user.id,
    )
    yield invitation
    delete_instance(session, invitation)