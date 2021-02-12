from datetime import datetime
import pytest

from app.routers.user import (
    create_user, disable_user, does_user_exist, enable_user, get_users
)
from app.database.models import User, UserEvent, Event
from app.routers.event import create_event

# -----------------------------------------------------
# Fixtures
# -----------------------------------------------------


@pytest.fixture
def new_user(session):
    user = create_user(
        session=session,
        username='new_test_username',
        password='new_test_password',
        email='new_test.email@gmail.com',
        language_id='english'
    )

    return user


# -----------------------------------------------------
# Tests
# -----------------------------------------------------


def test_disabling_user(new_user, session):
    """makes sure user is disabled
    and doesn't have any future events when disabled.
    also - makes sure that after a user is disabled,
    he can be easily enabled"""
    if disable_user(session, new_user.id):
        testing1 = session.query(User).get(new_user.id)
        assert testing1.disabled
        future_events = list(session.query(Event.id).join(UserEvent)
                             .filter(
                                 UserEvent.user_id == new_user.id,
                                 Event.start > datetime.now()
                                 ))
        assert len(future_events) == 0
        enable_user(session, new_user.id)
        assert not new_user.disabled
        # making sure that after disabling the user he can be easily enabled.
    else:
        user_owned_events = session.query(Event).join().filter(
            Event.start > datetime.now(), Event.owner_id == new_user.id
            )
        assert len(user_owned_events) > 0


def test_disabling_event_owning_user(new_user, session):
    # this test assures that an event-owning user can't disable itself.
    data = {
        'title': 'test title',
        'start': datetime.strptime('2021-01-01 15:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-01-02 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/875384596',
        'content': 'content',
        'owner_id': new_user.id,
    }

    create_event(session, **data)
    assert not disable_user(session, new_user.id)
    # making sure disabling user fails when it has events
    assert not new_user.disabled


class TestUser:

    def test_create_user(self, session):
        user = create_user(
            session=session,
            username='new_test_username',
            password='new_test_password',
            email='new_test.email@gmail.com',
            language_id=1
        )
        assert user.username == 'new_test_username'
        assert user.password == 'new_test_password'
        assert user.email == 'new_test.email@gmail.com'
        assert user.language_id == 1
        session.delete(user)
        session.commit()

    def test_get_users_success(self, user, session):
        assert get_users(username=user.username, session=session) == [user]
        assert get_users(password=user.password, session=session) == [user]
        assert get_users(email=user.email, session=session) == [user]

    def test_get_users_failure(self, session, user):
        assert get_users(username='wrong username', session=session) == []
        assert get_users(wrong_param=user.username, session=session) == []

    def test_does_user_exist_success(self, user, session):
        assert does_user_exist(username=user.username, session=session)
        assert does_user_exist(user_id=user.id, session=session)
        assert does_user_exist(email=user.email, session=session)

    def test_does_user_exist_failure(self, session):
        assert not does_user_exist(username='wrong username', session=session)
        assert not does_user_exist(session=session)

    def test_repr(self, user):
        assert user.__repr__() == f'<User {user.id}>'
