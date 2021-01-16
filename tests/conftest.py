from datetime import datetime

import pytest

from app.config import session
from app.database.models import Event, Invitation, User


def create_model(model_class, **kw):
    instance = model_class(**kw)
    session.add(instance)
    session.commit()
    return instance


def delete_instance(instance):
    session.delete(instance)
    session.commit()


@pytest.fixture
def user() -> User:
    test_user = create_model(
        User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
    )
    yield test_user
    delete_instance(test_user)


@pytest.fixture
def sender() -> User:
    sender = create_model(
        User,
        username='sender_email',
        password='sender_password',
        email='sender.email@gmail.com',
    )
    yield sender
    delete_instance(sender)


@pytest.fixture
def event(sender: User) -> Event:
    event = create_model(
        Event,
        title='test event',
        start=datetime.now(),
        end=datetime.now(),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(event)


@pytest.fixture
def invitation(event: Event, user: User) -> Event:
    invitation = create_model(
        Invitation,
        creation=datetime.now(),
        recipient=user,
        event=event,
        event_id=event.id,
        recipient_id=user.id,
    )
    yield invitation
    delete_instance(invitation)
