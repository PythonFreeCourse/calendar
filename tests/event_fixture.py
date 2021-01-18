from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, User
from tests.utils import create_model, delete_instance


today_date = datetime.today().replace(hour=0, minute=0, second=0)


@pytest.fixture
def event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='today_event',
        start=today_date,
        end=today_date,
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def today_event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 1',
        start=today_date + timedelta(hours=7),
        end=today_date + timedelta(hours=9),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def today_event_2(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 2',
        start=today_date + timedelta(hours=3),
        end=today_date + timedelta(days=2, hours=3),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def yesterday_event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 3',
        start=today_date - timedelta(hours=8),
        end=today_date,
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def next_week_event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 4',
        start=today_date + timedelta(days=7, hours=2),
        end=today_date + timedelta(days=7, hours=4),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def next_month_event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 5',
        start=today_date + timedelta(days=20, hours=4),
        end=today_date + timedelta(days=20, hours=6),
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def old_event(sender: User, session: Session) -> Event:
    event = create_model(
        session, Event,
        title='event 6',
        start=today_date - timedelta(days=5),
        end=today_date,
        content='test event',
        owner=sender,
        owner_id=sender.id,
    )
    yield event
    delete_instance(session, event)


@pytest.fixture
def user_event(user: User, session: Session) -> Event:
    """Only this event is created by "user" and not "sender"."""
    event = create_model(
        session, Event,
        title='event 7',
        start=today_date - timedelta(days=5),
        end=today_date,
        content='test event',
        owner=user,
        owner_id=user.id,
    )
    yield event
    delete_instance(session, event)