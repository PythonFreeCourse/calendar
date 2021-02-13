from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import pytest

from app.database.models import Event, User
from app.routers.dayview import DivAttributes
from app.routers.event import create_event


# TODO add user session login
@pytest.fixture
def user():
    return User(username='test1',
                email='user@email.com',
                password='1a2b3c4e5f',
                full_name='test me',
                language_id=1
                )


@pytest.fixture
def event1():
    start = datetime(year=2021, month=2, day=1, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=1, hour=9, minute=15)
    return Event(title='test1', content='test',
                 start=start, end=end, owner_id=1, all_day=False)


@pytest.fixture
def event2():
    start = datetime(year=2021, month=2, day=1, hour=13, minute=13)
    end = datetime(year=2021, month=2, day=1, hour=15, minute=46)
    return Event(title='test2', content='test',
                 start=start, end=end, owner_id=1, color='blue', all_day=False)


@pytest.fixture
def event3():
    start = datetime(year=2021, month=2, day=3, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=3, hour=9, minute=15)
    return Event(title='test3', content='test',
                 start=start, end=end, owner_id=1, all_day=False)


@pytest.fixture
def event_with_no_minutes_modified():
    start = datetime(year=2021, month=2, day=3, hour=7)
    end = datetime(year=2021, month=2, day=3, hour=8)
    return Event(title='test_no_modify', content='test',
                 start=start, end=end, owner_id=1, all_day=False)


@pytest.fixture
def multiday_event():
    start = datetime(year=2021, month=2, day=1, hour=13)
    end = datetime(year=2021, month=2, day=3, hour=13)
    return Event(title='test_multiday', content='test',
                 start=start, end=end, owner_id=1, color='blue', all_day=False)
def create_dayview_event(events, session, user):
    for event in events:
        create_event(
            db=session,
            title='test',
            start=event.start,
            end=event.end,
            owner_id=user.id,
            color=event.color
        )


def test_minutes_position_calculation(event_with_no_minutes_modified):
    div_attr = DivAttributes(event_with_no_minutes_modified)
    assert div_attr._minutes_position(div_attr.start_time.minute) is None
    assert div_attr._minutes_position(div_attr.end_time.minute) is None
    assert div_attr._minutes_position(0) is None
    assert div_attr._minutes_position(60) == 4


def test_div_attributes(event1):
    div_attr = DivAttributes(event1)
    assert div_attr.total_time == '07:05 - 09:15'
    assert div_attr.grid_position == '34 / 42'
    assert div_attr.length == 130
    assert div_attr.color == 'grey'


@pytest.mark.parametrize(
    "minutes,css_class,visiblity", [
        (90, 'title_size_small', True),
        (45, 'title_size_Xsmall', False),
        (30, 'title_size_tiny', False)
    ]
)
def test_font_size_attribute(minutes, css_class, visiblity):
    start = datetime(year=2021, month=2, day=3, hour=7)
    end = start + timedelta(minutes=minutes)
    event = Event(
        title='test', content='test',
        start=start, end=end, owner_id=1
    )
    div_attr = DivAttributes(event)
    assert div_attr.title_size_class == css_class
    assert div_attr.total_time_visible == visiblity


def test_div_attr_multiday(multiday_event):
    day = datetime(year=2021, month=2, day=1)
    assert DivAttributes(multiday_event, day).grid_position == '57 / 101'
    day += timedelta(hours=24)
    assert DivAttributes(multiday_event, day).grid_position == '1 / 101'
    day += timedelta(hours=24)
    assert DivAttributes(multiday_event, day).grid_position == '1 / 57'


def test_div_attributes_with_costume_color(event2):
    div_attr = DivAttributes(event2)
    assert div_attr.color == 'blue'


def test_wrong_timeformat(session, user, client, event1, event2, event3):
    create_dayview_event([event1, event2, event3], session=session, user=user)
    response = client.get('/day/1-2-2021')
    assert response.status_code == 404


def test_dayview_html(event1, event2, event3, session, user, client):
    create_dayview_event([event1, event2, event3], session=session, user=user)
    response = client.get("/day/2021-2-1")
    soup = BeautifulSoup(response.content, 'html.parser')
    assert 'FEBRUARY' in str(soup.find("div", {"id": "toptab"}))
    assert 'event1' in str(soup.find("div", {"id": "event1"}))
    assert 'event2' in str(soup.find("div", {"id": "event2"}))
    assert soup.find("div", {"id": "event3"}) is None


@pytest.mark.parametrize("day,grid_position", [("2021-2-1", '57 / 101'),
                                               ("2021-2-2", '1 / 101'),
                                               ("2021-2-3", '1 / 57')])
def test_dayview_html_with_multiday_event(multiday_event, session,
                                          user, client, day, grid_position):
    create_dayview_event([multiday_event], session=session, user=user)
    session.commit()
    response = client.get(f"/day/{day}")
    soup = BeautifulSoup(response.content, 'html.parser')
    grid_pos = f'grid-row: {grid_position};'
    assert grid_pos in str(soup.find("div", {"id": "event1"}))
