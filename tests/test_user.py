from datetime import datetime

from app.routers.user import (
    create_user, does_user_exist, get_users
)
from app.internal.user.availability import disable, enable
from app.internal.utils import save
from app.database.models import UserEvent, Event


def test_disabling_no_event_user(session, no_event_user):
    # users without any future event can disable themselves
    disable(session, no_event_user.id)
    assert no_event_user.disabled
    future_events = list(session.query(Event.id)
                         .join(UserEvent)
                         .filter(
                         UserEvent.user_id == no_event_user.id,
                         Event.start > datetime
                         .now()))
    assert not future_events
    # making sure that after disabling the user he can be easily enabled.
    enable(session, no_event_user.id)
    assert not no_event_user.disabled


def test_disabling_user_participating_event(
        session, no_event_user, event_example):
    """making sure only users who only participate in events
    can disable and enable themselves."""
    association = UserEvent(
        user_id=no_event_user.id,
        event_id=event_example.id
    )
    save(session, association)
    disable(session, no_event_user.id)
    assert no_event_user.disabled
    future_events = list(session.query(Event.id)
                         .join(UserEvent)
                         .filter(
                         UserEvent.user_id == no_event_user.id,
                         Event.start > datetime.now(),
                         Event.owner_id == no_event_user.id))
    assert not future_events
    enable(session, no_event_user.id)
    assert not no_event_user.disabled
    deleted_user_event_connection = session.query(UserEvent).filter(
        UserEvent.user_id == no_event_user.id,
        UserEvent.event_id == event_example.id).first()
    session.delete(deleted_user_event_connection)


def test_disabling_event_owning_user(session, event_owning_user):
    # making sure user owning events can't disable itself
    disable(session, event_owning_user.id)
    assert not event_owning_user.disabled


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
