from datetime import datetime
from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, Invitation, User
from app.internal.utils import create_model, delete_instance


@pytest.fixture
def invitation(
        event: Event, user: User, session: Session
) -> Generator[Invitation, None, None]:
    """Returns an Invitation object after being created in the database.

    Args:
        event: An Event instance.
        user: A user instance.
        session: A database connection.

    Returns:
        An Invitation object.
    """
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
