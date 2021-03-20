"""Tests for CRUD functions of the User model."""
from datetime import datetime
from typing import Any, Callable, Optional

import pytest
from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.database.crud import event as event_crud
from app.database.crud import user as crud
from app.database.models_v2 import User as UserOrm
from app.database.schemas_v2 import Event, Language, User, UserCreate
from app.internal.privacy import PrivacyKinds
from tests.crud.test_util import (
    get_boolean_getter_function,
    get_getter_function,
    get_setter_function,
)


def test_create(session_v2: Session, user_create: UserCreate):
    # Unique creation - successful.
    assert crud.create(session_v2, user_create)

    # Creation with duplicate unique fields - unsuccessful.
    assert crud.create(session_v2, user_create) is None


def test_delete(session_v2: Session, user_v2: User, event_v2: Event):
    events = crud.get_events(session_v2, user_v2)
    assert len(events) == 1

    # Deletion of existing user - successful.
    assert crud.delete(session_v2, user_v2)

    # User event's should be deleted automatically.
    events = crud.get_events(session_v2, user_v2)
    assert len(events) == 0

    # Verify event is not in the database.
    event_from_database = event_crud.get_by_id(session_v2, event_v2.id)
    assert event_from_database is None

    # Deletion of non-existing user - unsuccessful.
    assert crud.delete(session_v2, user_v2) is False


def test_get_database_user_by_id(session_v2: Session, user_v2: User):
    database_user = crud.get_database_user_by_id(session_v2, user_v2.id)
    assert isinstance(database_user, UserOrm)
    assert database_user.id == user_v2.id
    assert database_user.username == user_v2.username
    assert crud.get_by_id(session_v2, 2) is None


def test_get_by_id(session_v2: Session, user_v2: User):
    database_user = crud.get_by_id(session_v2, user_v2.id)
    assert isinstance(database_user, User)
    assert database_user.id == user_v2.id
    assert database_user.username == user_v2.username
    assert crud.get_by_id(session_v2, 2) is None


def test_get_by_username(session_v2: Session, user_v2: User):
    schema_model = crud.get_by_username(session_v2, user_v2.username)
    assert isinstance(schema_model, User)
    assert schema_model.id == user_v2.id
    assert schema_model.username == user_v2.username
    assert crud.get_by_username(session_v2, "bad username") is None


def test_get_by_email(session_v2: Session, user_v2: User):
    schema_model = crud.get_by_email(session_v2, "email@gmail.com")
    assert isinstance(schema_model, User)
    assert schema_model.id == user_v2.id
    assert schema_model.username == user_v2.username
    assert crud.get_by_email(session_v2, "bad email") is None


@pytest.mark.parametrize("number_of_users", [0, 1, 2])
def test_get_all_users(
    session_v2: Session,
    create_users: Callable[[str, str], Optional[User]],
    number_of_users: int,
):
    for i in range(number_of_users):
        create_users(f"username{i}", f"email{i}@gmail.com")
    assert len(crud.get_all(session_v2)) == number_of_users


COLUMNS_STANDARD_TESTS = [
    ("avatar", "file_path"),
    ("description", "description"),
    ("target_weight", 55.5),
]


@pytest.mark.parametrize("column_name, value", COLUMNS_STANDARD_TESTS)
def test_get_set_value_standard_fields(
    session_v2: Session,
    user_v2: User,
    column_name: str,
    value: Any,
):
    setter_function = get_setter_function(crud, column_name)
    assert setter_function(session_v2, user_v2, value)
    getter_function = get_getter_function(crud, column_name)
    assert getter_function
    assert getter_function(session_v2, user_v2) == value


COLUMNS_BOOLEAN_TESTS = [
    "active",
    "admin",
]


@pytest.mark.parametrize("column_name", COLUMNS_BOOLEAN_TESTS)
def test_get_set_value_boolean_fields(
    session_v2: Session,
    user_v2: User,
    column_name: str,
):
    for state in [True, False]:
        setter_function = get_setter_function(crud, column_name)
        assert setter_function(session_v2, user_v2, state)
        getter_function = get_boolean_getter_function(crud, column_name)
        assert getter_function(session_v2, user_v2) == state


COLUMN_UNIQUE_TESTS = [
    ("telegram_id", "TEST1234567TEST"),
    ("email", "test_email@gmail.com"),
    ("username", "test_username"),
]


@pytest.mark.parametrize("column_name, value", COLUMN_UNIQUE_TESTS)
def test_get_set_unique_columns(
    session_v2: Session,
    create_users: Callable[[str, str], Optional[User]],
    column_name: str,
    value: str,
):
    users = []
    for i in range(2):
        users.append(create_users(f"username{i}", f"email{i}@gmail.com"))

    user1 = users[0]
    user2 = users[1]
    assert user1
    assert user2

    getter_function = get_getter_function(crud, column_name)
    setter_function = get_setter_function(crud, column_name)

    # Set a unique value for user1.
    change_one = True
    assert setter_function(session_v2, user1, value) is change_one

    database_result_user1 = _get_getter_result(
        session_v2,
        user1,
        getter_function,
        column_name,
    )

    _validate_getter_result(database_result_user1, None, value, change_one)

    original_result_user2 = _get_getter_result(
        session_v2,
        user2,
        getter_function,
        column_name,
    )

    # User2 cannot have the same unique value.
    change_two = False
    assert setter_function(session_v2, user2, value) is change_two

    database_result_user2 = _get_getter_result(
        session_v2,
        user2,
        getter_function,
        column_name,
    )

    _validate_getter_result(
        database_result_user2,
        original_result_user2,
        value,
        change_two,
    )

    # Change the unique value for user1.
    change_three = True
    new_value = f"new_{value}"
    assert setter_function(session_v2, user1, new_value) is change_three

    database_result_user1 = _get_getter_result(
        session_v2,
        user1,
        getter_function,
        column_name,
    )

    _validate_getter_result(
        database_result_user1,
        None,
        new_value,
        change_three,
    )

    # User2 can now have the previously unavailable unique value.
    change_four = True
    assert setter_function(session_v2, user2, value) is change_four
    database_result_user2 = _get_getter_result(
        session_v2,
        user2,
        getter_function,
        column_name,
    )
    _validate_getter_result(database_result_user2, None, value, change_four)


EMAIL_TESTS = [
    (None, False),
    ("", False),
    ("b", False),
    ("b@", False),
    ("b@com", False),
    ("b@.com", False),
    ("@", False),
    ("@.com", False),
    ("b.com", False),
    ("b@c.com", True),
]


@pytest.mark.parametrize("email, is_valid", EMAIL_TESTS)
def test_get_set_email(
    session_v2: Session,
    user_v2: User,
    email: str,
    is_valid: bool,
):
    original_email = "email@gmail.com"
    assert crud.set_email(session_v2, user_v2, email) == is_valid
    database_email = crud.get_email(session_v2, user_v2)
    _validate_getter_result(database_email, original_email, email, is_valid)


FULL_NAME_TESTS = [
    (None, False),
    ("", False),
    ("b", False),
    ("ba", True),
    ("b" * 21, True),
]


@pytest.mark.parametrize("name, is_valid", FULL_NAME_TESTS)
def test_get_set_full_name(
    session_v2: Session,
    user_v2: User,
    name: str,
    is_valid: bool,
):
    original_full_name = user_v2.full_name
    assert crud.set_full_name(session_v2, user_v2, name) is is_valid
    _validate_getter_result(
        user_v2.full_name,
        original_full_name,
        name,
        is_valid,
    )


def test_get_set_language(session_v2: Session, user_v2: User):
    language = crud.get_language(session_v2, user_v2)
    assert language == Language(id=1, name="English", code="en")
    assert crud.set_language(session_v2, user_v2, 2)
    language = crud.get_language(session_v2, user_v2)
    assert language == Language(id=2, name="עברית", code="he")


PASSWORD_TESTS = [
    (None, False),
    ("", False),
    ("a", False),
    ("ab", False),
    ("a" * 21, False),
    (1, False),
    ("abc", True),
    ("abc123!@#$_", True),
]


@pytest.mark.parametrize("password, is_valid", PASSWORD_TESTS)
def test_set_password(
    session_v2: Session,
    user_v2: User,
    password: str,
    is_valid: bool,
):
    secret_password: Any
    try:
        secret_password = SecretStr(password)
    except TypeError:
        secret_password = password

    result = crud.set_password(session_v2, user_v2, secret_password)
    assert result is is_valid


PRIVACY_TESTS = [
    (None, False),
    ("", False),
    ("bad_key", False),
    (1, False),
    (PrivacyKinds.Public, True),
    (PrivacyKinds.Private, True),
    (PrivacyKinds.Hidden, True),
]


@pytest.mark.parametrize("privacy, is_valid", PRIVACY_TESTS)
def test_get_set_privacy(
    session_v2: Session,
    user_v2: User,
    privacy: Any,
    is_valid: bool,
):
    original_privacy = crud.get_privacy(session_v2, user_v2)
    assert crud.set_privacy(session_v2, user_v2, privacy) is is_valid
    database_privacy = crud.get_privacy(session_v2, user_v2)
    _validate_getter_result(
        database_privacy,
        original_privacy,
        privacy,
        is_valid,
    )


USERNAME_TESTS = [
    (None, False),
    ("", False),
    ("a", False),
    ("ab", False),
    ("a" * 21, False),
    ("abc%@", False),
    ("abc", True),
    ("abc12309_", True),
]


@pytest.mark.parametrize("username, is_valid", USERNAME_TESTS)
def test_set_username(
    session_v2: Session,
    user_v2: User,
    username: str,
    is_valid: bool,
):
    original_username = user_v2.username
    assert crud.set_username(session_v2, user_v2, username) is is_valid
    _validate_getter_result(
        user_v2.username,
        original_username,
        username,
        is_valid,
    )


@pytest.mark.parametrize("number_of_events", [0, 1, 2])
def test_get_owned_events(
    session_v2: Session,
    create_users: Callable[[str, str], Optional[User]],
    create_events: Callable[[int, datetime, datetime], Optional[Event]],
    number_of_events: int,
):
    user1 = create_users("username1", "email1@gmail.com")
    assert user1
    for i in range(number_of_events):
        create_events(user1.id, datetime.today(), datetime.today())
    events = crud.get_owned_events(session_v2, user1)
    assert len(events) == number_of_events

    user2 = create_users("username2", "email2@gmail.com")
    assert user2
    create_events(user2.id, datetime.today(), datetime.today())
    events2 = crud.get_owned_events(session_v2, user2)
    assert len(events2) == 1

    events = crud.get_owned_events(session_v2, user1)
    assert len(events) == number_of_events


def test_get_events(
    session_v2: Session,
    create_users: Callable[[str, str], Optional[User]],
    create_events: Callable[[int, datetime, datetime], Optional[Event]],
):
    user1 = create_users("username1", "email1@gmail.com")
    user2 = create_users("username2", "email2@gmail.com")
    user3 = create_users("username3", "email3@gmail.com")
    assert user1
    assert user2
    assert user3

    create_events(user1.id, datetime.today(), datetime.today())

    event2 = create_events(user1.id, datetime.today(), datetime.today())
    assert event2
    event_crud.add_member(session_v2, event2, user2)

    event3 = create_events(user2.id, datetime.today(), datetime.today())
    assert event3
    event_crud.add_member(session_v2, event3, user1)

    user1_events = crud.get_events(session_v2, user1)
    assert len(user1_events) == 3

    user2_events = crud.get_events(session_v2, user2)
    assert len(user2_events) == 2

    user3_events = crud.get_events(session_v2, user3)
    assert len(user3_events) == 0


def test_get_delete_google_calendar_events(
    session_v2: Session,
    user_v2: User,
    create_events: Callable[[int, datetime, datetime], Optional[Event]],
):
    number_of_events = 4
    number_of_google_events = 2
    events = []

    # Create number_of_events events.
    for i in range(number_of_events):
        event = create_events(user_v2.id, datetime.today(), datetime.today())
        assert event
        events.append(event)

    # Mark number_of_google_events events as Google Calendar events.
    for event in events[::2]:
        event_orm = event_crud.get_database_event_by_id(session_v2, event.id)
        assert event_orm
        event_orm.is_google_event = True
        session_v2.commit()

    # Verify number of events is number_of_events.
    all_events = crud.get_events(session_v2, user_v2)
    assert len(all_events) == number_of_events

    # Verify number of Google events is number_of_google_events.
    google_events = crud.get_google_calender_events(session_v2, user_v2)
    assert len(google_events) == number_of_google_events

    assert crud.delete_all_google_calendar_events(session_v2, user_v2)

    # Verify there are no more Google events.
    google_events = crud.get_google_calender_events(session_v2, user_v2)
    assert len(google_events) == 0

    # Verify current number of events is
    # number_of_events - number_of_google_events.
    remaining_events = number_of_events - number_of_google_events
    all_events = crud.get_events(session_v2, user_v2)
    owned_events = crud.get_owned_events(session_v2, user_v2)
    assert (
        len(all_events) == remaining_events
        and len(owned_events) == remaining_events
    )


def _get_getter_result(
    session_v2: Session,
    user: User,
    getter: Optional[Callable],
    column_name: str,
) -> Any:
    if column_name == "username":
        return user.username
    else:
        assert getter
        return getter(session_v2, user)


def _validate_getter_result(
    current_value: Any,
    original_value: Any,
    new_value: str,
    is_valid: bool,
):
    if is_valid:
        assert current_value == new_value
    else:
        assert current_value == original_value
