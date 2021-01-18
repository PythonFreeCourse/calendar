from datetime import datetime

import pytest

from app.main import app
from app.routers.dayview import Event
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    client = TestClient(app)
    return client

@pytest.fixture
def event():
    event_id = 123
    color = 'red'
    content = 'nothing'
    start = "03/2/2021 4:05"
    end = "03/2/2021 4:20"
    event = Event(id=event_id, color=color,
                  content=content,start_datetime=start,
                  end_datetime=end)
    return event
    

def test_new_event(event):
    assert event.id == 123
    assert event.color == 'red'
    assert event.content == 'nothing'
    assert event.total_time == '04:05 - 04:20'
    assert event.grid_position == '22 / 23'
    assert event.length == 15


def test_dayview_html(client, event):
    events = [{"id":event.id, "color":event.color,
               "content":event.content,
               "start_datetime":"3/2/2021 04:05",
               "end_datetime":"3/2/2021 04:20",
               }]
    day = {"year":2021, "month":2, "day":3, "events":events}
    response = client.post("/dayview", json=day)
    res = response.content.decode("utf-8") 
    assert 'grid-row: 22 / 23;' in res
    assert '<div id="event123"' in res 


def test_few_events_at_once(client, event):
    events = [{"id": "21",
              "color":"navy",
              "start_datetime": "3/2/2021 04:10",
              "end_datetime": "3/2/2021 06:50",
              "content": "nothing to do all day"},
              {"id": "24",
              "color":"navy",
              "start_datetime": "3/2/2021 07:10",
              "end_datetime": "3/2/2021 09:50",
              "content": "nothing to do all day"},]
    day = {"year":2021, "month":2, "day":3, "events":events}
    response = client.post("/dayview", json=day)
    res = response.content.decode("utf-8") 
    assert '<div id="event21"' in res
    assert '<div id="event24"' in res
