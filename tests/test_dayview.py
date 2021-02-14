from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import pytest

from app.database.models import Event
from app.routers.dayview import CurrentTimeAttributes, DivAttributes, EventsAttributes
from app.routers.event import create_event


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
    div_attr = EventsAttributes(event_with_no_minutes_modified)
    assert div_attr._minutes_position(div_attr.start_time.minute) is None
    assert div_attr._minutes_position(div_attr.end_time.minute) is None
    assert div_attr._minutes_position(0) is None
    assert div_attr._minutes_position(60)['min_position'] == 4


def test_event_attributes(event1):
    div_attr = EventsAttributes(event1)
    assert div_attr.total_time == '07:05 - 09:15'
    assert div_attr.grid_position == '34 / 42'
    assert div_attr.length == 130
    assert div_attr.color == 'grey'


def test_current_time_gets_today_attributes():
    today = datetime.now()
    current_attr = CurrentTimeAttributes(today)
    assert current_attr.dayview_date == today.date()
    assert current_attr.is_viewed is True


def test_current_time_gets_not_today_attributes(not_today):
    current_attr = CurrentTimeAttributes(not_today)
    assert str(current_attr.dayview_date) == '2012-12-12'
    assert current_attr.is_viewed is False

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
    div_attr = EventsAttributes(event)
    assert div_attr.title_size_class == css_class
    assert div_attr.total_time_visible == visiblity


def test_div_attr_multiday(multiday_event):
    day = datetime(year=2021, month=2, day=1)
    assert EventsAttributes(multiday_event, day).grid_position == '57 / 101'
    day += timedelta(hours=24)
    assert EventsAttributes(multiday_event, day).grid_position == '1 / 101'
    day += timedelta(hours=24)
    assert EventsAttributes(multiday_event, day).grid_position == '1 / 57'


def test_div_attributes_with_costume_color(event2):
    div_attr = EventsAttributes(event2)
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
