from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, User
from tests.utils import create_model, delete_instance


@pytest.fixture
def event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='test event',
        start=datetime.now(),
        end=datetime.now(),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)