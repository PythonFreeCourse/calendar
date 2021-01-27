from datetime import datetime

import pytest
from app.database.models import Event
from app.routers.event import update_event
from starlette.status import HTTP_302_FOUND, HTTP_404_NOT_FOUND

CORRECT_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-01-28',
    'start_time': '15:59',
    'end_date': '2021-01-27',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'https://us02web.zoom.us/j/875384596',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

WRONG_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-01-28',
    'start_time': '15:59',
    'end_date': '2021-01-27',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'not a zoom link',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

INVALID_UPDATE_OPTIONS = [
    {}, {"test": "test"}, {"start": "20.01.2020"},
    {"start": datetime(2020, 2, 2), "end": datetime(2020, 1, 1)},
    {"start": datetime(2030, 2, 2)}, {"end": datetime(1990, 1, 1)},
]


class TestEvent:
    def test_eventedit(self, client):
        response = client.get("/event/edit")
        assert response.ok
        assert b"Edit Event" in response.content

    def test_eventview_with_id(self, client):
        response = client.get("/event/view/1")
        assert response.ok
        assert b"View Event" in response.content

    def test_eventview_without_id(self, client):
        response = client.get("/event/view")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_eventedit_post_correct(self, client, user):
        response = client.post("/event/edit",
                               data=CORRECT_EVENT_FORM_DATA)
        assert response.status_code == HTTP_302_FOUND
        assert '/event/view/' in response.headers['location']

    def test_eventedit_post_wrong(self, client, user):
        response = client.post("/event/edit",
                               data=WRONG_EVENT_FORM_DATA)
        assert response.json()['detail'] == 'VC type with no valid zoom link'

    @staticmethod
    @pytest.mark.parametrize("data", INVALID_UPDATE_OPTIONS)
    def test_invalid_update(event, data, session):
        assert update_event(event_id=event.id,
                            event=data, db=session) is None

    @staticmethod
    def test_successful_update(event, session):
        data = {
            "title": "successful",
            "start": datetime(2021, 1, 20),
            "end": datetime(2021, 1, 21),
        }
        assert isinstance(update_event(1, data, session), Event)
        assert "successful" in update_event(
            event_id=event.id, event=data, db=session).title

    @staticmethod
    def test_update_db_close(event):
        data = {"title": "Problem connecting to db", }
        assert update_event(event_id=event.id,
                            event=data, db=None) is None

    @staticmethod
    def test_update_event_does_not_exist(event, session):
        data = {
            "content": "An update test for an event does not exist"
        }
        assert update_event(
            event_id=500, event=data, db=session) is None

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'
