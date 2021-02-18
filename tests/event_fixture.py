from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.database.models import Category, Event, User
from app.routers.event import create_event

today_date = datetime.today().replace(hour=0, minute=0, second=0)


@pytest.fixture
def event(sender: User, category: Category, session: Session) -> Event:
    return create_event(
        db=session,
        title='event',
        start=today_date,
        end=today_date,
        content='test event',
        owner_id=sender.id,
        location="Some random location",
        vc_link=None,
        category_id=category.id,
    )


@pytest.fixture
def today_event(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 1',
        start=today_date + timedelta(hours=7),
        end=today_date + timedelta(hours=9),
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def today_event_2(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 2',
        start=today_date + timedelta(hours=3),
        end=today_date + timedelta(days=2, hours=3),
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def yesterday_event(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 3',
        start=today_date - timedelta(hours=8),
        end=today_date,
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def next_week_event(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 4',
        start=today_date + timedelta(days=7, hours=2),
        end=today_date + timedelta(days=7, hours=4),
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def next_month_event(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 5',
        start=today_date + timedelta(days=20, hours=4),
        end=today_date + timedelta(days=20, hours=6),
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def old_event(sender: User, session: Session) -> Event:
    return create_event(
        db=session,
        title='event 6',
        start=today_date - timedelta(days=5),
        end=today_date - timedelta(days=1),
        all_day=False,
        content='test event',
        owner_id=sender.id,
    )


@pytest.fixture
def all_day_event(sender: User, category: Category, session: Session) -> Event:
    return create_event(
        db=session,
        title='event',
        start=today_date,
        end=today_date,
        all_day=True,
        content='test event',
        owner_id=sender.id,
        location="Some random location",
        category_id=category.id,
    )
