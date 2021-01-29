from datetime import datetime

import pytest
from app.database.models import Event
from app.routers.event import by_id, update_event
from starlette import status

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
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

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

    def test_successful_deletion(self, event_test_client, session, event):
        respons = event_test_client.delete("/event/1")
        assert respons.ok
        assert by_id(db=session, event_id=1) is None

    def test_delete_failed(self, event_test_client, event):
        respons = event_test_client.delete("/event/2")
        assert respons.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
