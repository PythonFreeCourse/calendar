from datetime import datetime
import pytest

from app.routers.user import (
    create_user, does_user_exist, get_users
)
from app.internal.user.availability import disable, enable
from app.internal.utils import save
from app.database.models import UserEvent, Event
from app.routers.event import create_event


@pytest.fixture
def user1(session):
    # a user made for testing who doesn't own any event.
    user = create_user(
        session=session,
        username='new_test_username',
        password='new_test_password',
        email='new2_test.email@gmail.com',
        language_id='english'
    )

    return user


@pytest.fixture
def user2(session):
    # a user made for testing who already owns an event.
    user = create_user(
        session=session,
        username='new_test_username2',
        password='new_test_password2',
        email='new_test_love231.email@gmail.com',
        language_id='english'
    )

    data = {
        'title': 'user2 event',
        'start': datetime.strptime('2021-05-05 14:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-05-05 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/875384596',
        'content': 'content',
        'owner_id': user.id,
    }

    create_event(session, **data)

    return user


@pytest.fixture
def event1(session, user2):
    data = {
        'title': 'test event title',
        'start': datetime.strptime('2021-05-05 14:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-05-05 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/87538459r6',
        'content': 'content',
        'owner_id': user2.id,
    }

    event = create_event(session, **data)
    return event


def test_disabling_no_event_user(session, user1):
    # users without any future event can disable themselves
    disable(session, user1.id)
    assert user1.disabled
    future_events = list(session.query(Event.id)
                         .join(UserEvent)
                         .filter(
                         UserEvent.user_id == user1.id,
                         Event.start > datetime
                         .now()))
    assert not future_events
    # making sure that after disabling the user he can be easily enabled.
    enable(session, user1.id)
    assert not user1.disabled


def test_disabling_user_participating_event(
        session, user1, event1):
    """making sure only users who only participate in events
    can disable and enable themselves."""
    association = UserEvent(
        user_id=user1.id,
        event_id=event1.id
    )
    save(session, association)
    disable(session, user1.id)
    assert user1.disabled
    future_events = list(session.query(Event.id)
                         .join(UserEvent)
                         .filter(
                         UserEvent.user_id == user1.id,
                         Event.start > datetime.now(),
                         Event.owner_id == user1.id))
    assert not future_events
    enable(session, user1.id)
    assert not user1.disabled
    deleted_user_event_connection = session.query(UserEvent).filter(
        UserEvent.user_id == user1.id,
        UserEvent.event_id == event1.id).first()
    session.delete(deleted_user_event_connection)


def test_disabling_event_owning_user(session, user2):
    # making sure user owning events can't disable itself
    disable(session, user2.id)
    assert not user2.disabled


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
