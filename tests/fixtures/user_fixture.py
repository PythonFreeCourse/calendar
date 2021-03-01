from datetime import datetime
from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.schemas import UserCreate
from app.internal.utils import create_model, delete_instance
from app.routers.event import create_event
from app.routers.register import _create_user, create_user


@pytest.fixture
async def user(session: Session) -> Generator[User, None, None]:
    schema = UserCreate(
        username="test_username",
        password="test_password",
        confirm_password="test_password",
        email="test.email@gmail.com",
        full_name="test_full_name",
        description="test_description",
        language_id=1,
        target_weight=60,
    )
    mock_user = await create_user(session, schema)
    yield mock_user
    delete_instance(session, mock_user)


@pytest.fixture
def sender(session: Session) -> Generator[User, None, None]:
    mock_user = create_model(
        session,
        User,
        username="sender_username",
        password="sender_password",
        email="sender.email@gmail.com",
        language_id=1,
    )
    yield mock_user
    delete_instance(session, mock_user)


@pytest.fixture
def no_event_user(session):
    """a user made for testing who doesn't own any event."""
    user = _create_user(
        session=session,
        username="new_test_username",
        password="new_test_password",
        email="new2_test.email@gmail.com",
        language_id="english",
    )

    return user


@pytest.fixture
def event_owning_user(session):
    """a user made for testing who already owns an event."""
    user = _create_user(
        session=session,
        username="new_test_username2",
        password="new_test_password2",
        email="new_test_love231.email@gmail.com",
        language_id="english",
    )

    data = {
        "title": "event_owning_user event",
        "start": datetime.strptime("2021-05-05 14:59", "%Y-%m-%d %H:%M"),
        "end": datetime.strptime("2021-05-05 15:01", "%Y-%m-%d %H:%M"),
        "location": "https://us02web.zoom.us/j/875384596",
        "content": "content",
        "owner_id": user.id,
    }

    create_event(session, **data)

    return user


@pytest.fixture
def user1(session):
    """another user made for testing"""
    user = _create_user(
        session=session,
        username="user2user2",
        password="verynicepass",
        email="trulyyours1.email@gmail.com",
        language_id="english",
    )
    return user
