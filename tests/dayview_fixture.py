from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.database.models import Event, User

@pytest.fixture
def event1():
    start = datetime(year=2021, month=2, day=1, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=1, hour=9, minute=15)
    return Event(title='test1', content='test',
                 start=start, end=end, owner_id=1)


@pytest.fixture
def event2():
    start = datetime(year=2021, month=2, day=1, hour=13, minute=13)
    end = datetime(year=2021, month=2, day=1, hour=15, minute=46)
    return Event(title='test2', content='test',
                 start=start, end=end, owner_id=1, color='blue')


@pytest.fixture
def event3():
    start = datetime(year=2021, month=2, day=3, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=3, hour=9, minute=15)
    return Event(title='test3', content='test',
                 start=start, end=end, owner_id=1)

@pytest.fixture
def event1():
    start = datetime(year=2021, month=2, day=1, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=1, hour=9, minute=15)
    return Event(title='test1', content='test',
                 start=start, end=end, owner_id=1)


@pytest.fixture
def event2():
    start = datetime(year=2021, month=2, day=1, hour=13, minute=13)
    end = datetime(year=2021, month=2, day=1, hour=15, minute=46)
    return Event(title='test2', content='test',
                 start=start, end=end, owner_id=1, color='blue')


@pytest.fixture
def event3():
    start = datetime(year=2021, month=2, day=3, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=3, hour=9, minute=15)
    return Event(title='test3', content='test',
                 start=start, end=end, owner_id=1)


@pytest.fixture
def event_with_no_minutes_modified():
    start = datetime(year=2021, month=2, day=3, hour=7)
    end = datetime(year=2021, month=2, day=3, hour=8)
    return Event(title='test_no_modify', content='test',
                 start=start, end=end, owner_id=1)


@pytest.fixture
def multiday_event():
    start = datetime(year=2021, month=2, day=1, hour=13)
    end = datetime(year=2021, month=2, day=3, hour=13)
    return Event(title='test_multiday', content='test',
                 start=start, end=end, owner_id=1, color='blue')
