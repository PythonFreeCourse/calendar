from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Event, Invitation, User, Base


@pytest.fixture(scope="session")
def engine():
    print("TestCase: Using sqlite database")
    return create_engine('sqlite:///', echo=False)


@pytest.fixture(scope="session")
def session(engine):
    sessionmaker_ = sessionmaker(bind=engine)
    session = sessionmaker_()
    Base.metadata.create_all(engine)

    yield session

    session.close()


@pytest.fixture
def user(session: Session) -> User:
    test_user = create_model(
        session, User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
    )
    yield test_user
    delete_instance(session, test_user)


@pytest.fixture
def sender(session: Session) -> User:
    sender = create_model(
        session, User,
        username='sender_email',
        password='sender_password',
        email='sender.email@gmail.com',
    )
    yield sender
    delete_instance(session, sender)


@pytest.fixture
def event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='test event',
        start=datetime.now(),
        end=datetime.now(),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def invitation(event: Event, user: User, session: Session) -> Event:
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


def create_model(session: Session, model_class, **kw):
    instance = model_class(**kw)
    session.add(instance)
    session.commit()
    return instance


def delete_instance(session: Session, instance):
    session.delete(instance)
    session.commit()
