from bs4 import BeautifulSoup
import pytest

from app.routers.event import create_event
from app.routers.weekview import get_week_dates


def create_weekview_event(events, session, user):
    for event in events:
        create_event(
            db=session,
            title='test',
            start=event.start,
            end=event.end,
            owner_id=user.id,
            color=event.color
        )


def test_get_week_dates(weekdays, sunday):
    week_dates = list(get_week_dates(sunday))
    for i in range(6):
        assert week_dates[i].strftime('%A') == weekdays[i]


def test_weekview_day_names(session, user, client, weekdays):
    response = client.get("/week/2021-1-3")
    soup = BeautifulSoup(response.content, 'html.parser')
    day_divs = soup.find_all("div", {"class": 'day-name'})
    for i in range(6):
        assert weekdays[i][:3].upper() in str(day_divs[i])


def test_weekview_day_dates(session, user, client, sunday):
    response = client.get("/week/2021-1-3")
    soup = BeautifulSoup(response.content, 'html.parser')
    day_divs = soup.find_all("span", {"class": 'date-nums'})
    week_dates = list(get_week_dates(sunday))
    for i in range(6):
        time_str = f'{week_dates[i].day} / {week_dates[i].month}'
        assert time_str in day_divs[i]


@pytest.mark.parametrize(
    "date,event",
    [("2021-1-31", 'event1'),
     ("2021-1-31", 'event2'),
     ("2021-2-3", 'event3')]
)
def test_weekview_html_events(
    event1, event2, event3, session, user, client, date, event
):
    create_weekview_event([event1, event2, event3], session=session, user=user)
    response = client.get(f"/week/{date}")
    soup = BeautifulSoup(response.content, 'html.parser')
    assert event in str(soup.find("div", {"id": event}))
