"""Fixtures for schemas and models v.2"""
from datetime import datetime
from typing import Callable, Generator, Optional

import pytest
from pydantic import EmailStr, SecretStr
from sqlalchemy.orm import Session

from app.database.crud import event as event_crud
from app.database.crud import user as user_crud
from app.database.models_v2 import Base
from app.database.schemas_v2 import (
    Event,
    EventCreate,
    Language,
    User,
    UserCreate,
)
from app.internal.privacy import PrivacyKinds
from tests.conftest import get_test_db, test_engine


@pytest.fixture
def event_create(user_v2: User) -> EventCreate:
    """Returns an EventCreate entity fixture.

    Args:
        user_v2: A User entity.

    Returns:
        An EventCreate object.
    """
    return EventCreate(
        date_start=datetime.today(),
        date_end=datetime.today(),
        color="red",
        content="content",
        emotion="emotion",
        image="event_image.png",
        invited_emails="invite1@gmail.com, invite2@gmail.com",
        is_available=False,
        is_all_day=True,
        is_google_event=False,
        latitude=32.0853,
        location="Tel Aviv",
        longitude=34.7818,
        owner_id=user_v2.id,
        privacy=PrivacyKinds.Public,
        title="title",
        video_chat_link="https://www.link.com",
    )


@pytest.fixture
def event_v2(
    event_create: EventCreate,
    create_events: Callable[
        [int, datetime, datetime],
        Optional[Event],
    ],
) -> Generator[Optional[Event], None, None]:
    """Yields a single Event entity fixture.

    This is a convenience wrapper when there is only one Event entity needed
    for tests.

    Args:
        event_create: The EventCreate fixture.
        create_events: A generator which creates database Event entities.

    Yields:
        A User entity.
    """
    event = create_events(
        event_create.owner_id,
        event_create.date_start,
        event_create.date_end,
    )
    yield event


@pytest.fixture
def create_events(
    session_v2: Session,
    event_create: EventCreate,
) -> Generator[
    Callable[[int, datetime, datetime], Optional[Event]],
    None,
    None,
]:
    """Yields a function fixture which creates Event entities.

    Args:
        session_v2: The database connection fixture.
        event_create: The EventCreate fixture.

    Returns:
        An Event creation function fixture.
    """
    created_events = []

    def _create_events(
        owner_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[Event]:
        """Returns an Event which was saved in the database.

        Args:
            owner_id: The ID of the User who created the Event.
            start_date: The start date of the Event.
            end_date: The end date of the Event.

        Returns:
            An Event entity.
        """
        event_create.owner_id = owner_id
        event_create.date_start = start_date
        event_create.date_end = end_date

        event = event_crud.create(session_v2, event_create)
        created_events.append(event)
        return event

    yield _create_events

    for created_event in created_events:
        if created_event:
            event_crud.delete(session_v2, created_event)


@pytest.fixture
def language():
    """Returns a Language entity fixture."""
    return Language(id=1, name="English", code="en")


@pytest.fixture
def session_v2() -> Generator[Session, None, None]:
    """Yields a Session entity fixture to connect to the database.

    Additionally, the database tables are created before usage and destroyed
    when tests are completed.

    Yields:
        A Session object.
    """
    Base.metadata.create_all(bind=test_engine)
    session = get_test_db()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def user_create() -> UserCreate:
    """Returns a UserCreate entity fixture."""
    return UserCreate(
        username="username",
        full_name="full_name",
        password="12345",
        confirm_password=SecretStr("12345"),
        email=EmailStr("email@gmail.com"),
    )


@pytest.fixture
def user_v2(
    user_create,
    create_users: Callable[[str, str], Optional[User]],
) -> Generator[Optional[User], None, None]:
    """Yields a single User entity fixture.

    This is a convenience wrapper when there is only one User entity needed
    for tests.

    Args:
        user_create: The UserCreate fixture.
        create_users: A generator which creates database User entities.

    Yields:
        A User entity.
    """
    user = create_users(user_create.username, user_create.email)
    yield user


@pytest.fixture
def create_users(
    session_v2: Session,
    user_create: UserCreate,
) -> Generator[Callable[[str, str], Optional[User]], None, None]:
    """Yields a function fixture which creates User entities.

    Args:
        session_v2: The database connection fixture.
        user_create: The UserCreate fixture.

    Returns:
        A User creation function fixture.
    """
    created_users = []

    def _create_users(username: str, email: str) -> Optional[User]:
        """Returns a User which was saved in the database.

        Args:
            username: The User's unique username.
            email: The User's unique email address.

        Returns:
            A User entity.
        """
        user_create.username = username
        user_create.email = EmailStr(email)

        user = user_crud.create(session_v2, user_create)
        created_users.append(user)
        return user

    yield _create_users

    for created_user in created_users:
        if created_user:
            user_crud.delete(session_v2, created_user)
