"""Tests for CRUD functions of the Event model."""
from datetime import datetime
from typing import Callable, Optional

import pytest
from sqlalchemy.orm import Session

from app.database.crud import event as crud
from app.database.crud import user as user_crud
from app.database.schemas_v2 import Event, EventAll, EventCreate, User
from tests.crud.test_util import (
    get_attribute_value,
    get_boolean_getter_function,
    get_getter_function,
)


def test_create_event(session_v2: Session, event_create: EventCreate):
    assert crud.create(session_v2, event_create)


def test_delete(session_v2: Session, event_v2: Event):
    # Deletion of existing event - successful.
    assert crud.delete(session_v2, event_v2)

    # Deletion of non-existing event - unsuccessful.
    assert crud.delete(session_v2, event_v2) is False


def test_get_by_id(session_v2: Session, event_v2: Event):
    database_event = crud.get_by_id(session_v2, event_v2.id)
    assert database_event
    assert database_event.owner_id == event_v2.owner_id
    assert database_event.date_end == event_v2.date_end
    assert crud.get_by_id(session_v2, 2) is None


@pytest.mark.parametrize("number_of_events", [0, 1, 2])
def test_get_all_events(
    session_v2: Session,
    create_events: Callable[[int, datetime, datetime], Optional[Event]],
    number_of_events: int,
):
    for i in range(number_of_events):
        create_events(1, datetime.today(), datetime.today())
    assert len(crud.get_all(session_v2)) == number_of_events


def test_update_event(
    session_v2: Session,
    event_create: EventCreate,
    event_v2: Event,
):
    event_all = EventAll(**event_create.dict(), id=event_v2.id)
    event_all.title = "updated title"
    event_all.location = "updated location"

    event_from_database = crud.get_by_id(session_v2, event_v2.id)
    assert event_from_database
    current_title = event_from_database.title
    current_location = crud.get_location(session_v2, event_v2)
    assert crud.update_event(session_v2, event_all)

    event_from_database = crud.get_by_id(session_v2, event_v2.id)
    assert event_from_database
    updated_title = event_from_database.title
    updated_location = crud.get_location(session_v2, event_v2)

    assert current_title != updated_title and updated_title == event_all.title

    assert (
        current_location != updated_location
        and updated_location == event_all.location
    )


COLUMNS_BASE_TESTS = [
    "title",
    "owner_id",
    "date_start",
    "date_end",
    "is_all_day",
]


@pytest.mark.parametrize("column_name", COLUMNS_BASE_TESTS)
def test_get_value_base_fields(
    session_v2: Session,
    event_create: EventCreate,
    event_v2: Event,
    column_name: str,
):
    value_from_create = get_attribute_value(event_create, column_name)
    value_from_database = get_attribute_value(event_v2, column_name)
    assert value_from_create == value_from_database


COLUMNS_STANDARD_TESTS = [
    "color",
    "content",
    "emotion",
    "image",
    "invited_emails",
    "latitude",
    "location",
    "longitude",
    "privacy",
    "video_chat_link",
]


@pytest.mark.parametrize("column_name", COLUMNS_STANDARD_TESTS)
def test_get_value_standard_fields(
    session_v2: Session,
    event_create: EventCreate,
    event_v2: Event,
    column_name: str,
):
    getter_function = get_getter_function(crud, column_name)
    value = getattr(event_create, column_name)
    assert getter_function
    assert getter_function(session_v2, event_v2) == value


COLUMNS_BOOLEAN_TESTS = [
    "available",
    "google_event",
]


@pytest.mark.parametrize("column_name", COLUMNS_BOOLEAN_TESTS)
def test_get_value_boolean_fields(
    session_v2: Session,
    event_create: EventCreate,
    event_v2: Event,
    column_name: str,
):
    getter_function = get_boolean_getter_function(crud, column_name)
    value = getattr(event_create, f"is_{column_name}")
    assert getter_function
    assert getter_function(session_v2, event_v2) == value


def test_get_change_owner(
    session_v2: Session,
    event_v2: Event,
    create_users: Callable[[str, str], Optional[User]],
):
    original_owner = crud.get_owner(session_v2, event_v2)
    assert original_owner
    original_owner_events = user_crud.get_events(
        session_v2,
        original_owner,
    )

    original_owner_owned_events = user_crud.get_owned_events(
        session_v2,
        original_owner,
    )

    # Verify original values are 1.
    assert len(original_owner_events) == 1
    assert len(original_owner_owned_events) == 1

    user2 = create_users("user2", "email2@gmail.com")
    assert user2

    new_user_events = user_crud.get_events(session_v2, user2)
    new_user_owned_events = user_crud.get_owned_events(session_v2, user2)

    # Verify default values are 0.
    assert len(new_user_events) == 0
    assert len(new_user_owned_events) == 0

    assert crud.change_owner(session_v2, event_v2, user2.id)
    new_owner = crud.get_owner(session_v2, event_v2)
    new_owner_events = user_crud.get_events(session_v2, user2)
    new_owner_owned_events = user_crud.get_owned_events(session_v2, user2)

    # Verify new owner changed and values are updated to 1.
    assert new_owner == user2
    assert len(new_owner_events) == 1
    assert len(new_owner_owned_events) == 1

    original_owner_events = user_crud.get_events(
        session_v2,
        original_owner,
    )
    original_owner_owned_events = user_crud.get_owned_events(
        session_v2,
        original_owner,
    )

    # Verify original_owner values are updated.
    assert len(original_owner_events) == 1
    assert len(original_owner_owned_events) == 0


def test_get_add_delete_members(
    session_v2: Session,
    create_users: Callable[[str, str], Optional[User]],
    create_events: Callable[[int, datetime, datetime], Optional[Event]],
):
    user1 = create_users("username1", "email1@gmail.com")
    assert user1

    event = create_events(user1.id, datetime.today(), datetime.today())
    assert event

    # Owner should be the only member.
    members = crud.get_members(session_v2, event)
    assert len(members) == 1

    user2 = create_users("username2", "email2@gmail.com")
    assert user2

    # Add a new user.
    assert crud.add_member(session_v2, event, user2)
    members = crud.get_members(session_v2, event)
    assert len(members) == 2

    # Try and re-add the same users. It should fail.
    crud.add_member(session_v2, event, user1)
    members = crud.get_members(session_v2, event)
    assert len(members) == 2

    crud.add_member(session_v2, event, user2)
    members = crud.get_members(session_v2, event)
    assert len(members) == 2

    # Remove user. Only owner left.
    assert crud.remove_member(session_v2, event, user2)
    members = crud.get_members(session_v2, event)
    assert len(members) == 1
