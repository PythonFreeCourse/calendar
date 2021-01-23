from datetime import datetime

import pytest
from app.database.models import Event
from app.routers.event import update_event


INVALID_UPDATE_OPTIONS = [
    {}, {"test": "test"}, {"start": "20.01.2020"},
    {"start": datetime(2020, 2, 2), "end": datetime(2020, 1, 1)},
    {"start": datetime(2030, 2, 2)}, {"end": datetime(1990, 1, 1)},
]


def test_eventedit(client):
    response = client.get("/event/edit")
    assert response.status_code == 200
    assert b"Edit Event" in response.content


def test_eventview_with_id(client):
    response = client.get("/event/view/1")
    assert response.status_code == 200
    assert b"View Event" in response.content


def test_eventview_without_id(client):
    response = client.get("/event/view")
    assert response.status_code == 404


@pytest.mark.parametrize("data", INVALID_UPDATE_OPTIONS)
def test_invalid_update(event, data, session):
    assert update_event(event_id=1, event_dict=data, db=session) is None


def test_successful_update(event, session):
    data = {
        "title": "successful",
        "start": datetime(2021, 1, 20),
        "end": datetime(2021, 1, 21),
    }
    assert type(update_event(1, data, session)) == Event
    assert "successful" in update_event(
        event_id=1, event_dict=data, db=session).title


def test_update_db_close(event):
    data = {
        "title": "Problem connecting to db",
    }
    assert update_event(event_id=1, event_dict=data, db=None) is None


def test_update_event_does_not_exist(event, session):
    data = {
        "content": "An update test for an event does not exist"
    }
    assert update_event(event_id=500, event_dict=data, db=session) is None
