import pytest
from sqlalchemy.orm import Session

from app.database.models import Message, User
from app.internal.utils import create_model, delete_instance


@pytest.fixture
def message(user: User, session: Session) -> Message:
    invitation = create_model(
        session,
        Message,
        body="A test message",
        link="#",
        recipient_id=user.id,
    )
    yield invitation
    delete_instance(session, invitation)


@pytest.fixture
def sec_message(user: User, session: Session) -> Message:
    invitation = create_model(
        session,
        Message,
        body="A test message",
        link="#",
        recipient_id=user.id,
    )
    yield invitation
    delete_instance(session, invitation)
