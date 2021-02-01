from datetime import datetime

import pytest
from app.database.models import Event
from app.routers.event import (by_id, delete_event, is_change_dates_allowed,
                               update_event)
from fastapi import HTTPException
from starlette import status

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
    {}, {"test": "test"},
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

    def test_eventedit_post_correct(self, event_test_client, user):
        response = event_test_client.post(
            event_test_client.app.url_path_for(
                'create_new_event'), data=CORRECT_EVENT_FORM_DATA)
        assert response.ok
        assert response.status_code == status.HTTP_302_FOUND
        assert (event_test_client.app.url_path_for(
            'eventview', id=1).strip('1') in response.headers['location'])

    def test_eventedit_post_wrong(self, event_test_client, user):
        response = event_test_client.post(
            event_test_client.app.url_path_for(
                'create_new_event'), data=WRONG_EVENT_FORM_DATA)
        assert response.json()['detail'] == 'VC type with no valid zoom link'

    @pytest.mark.parametrize("data", INVALID_UPDATE_OPTIONS)
    def test_invalid_update(self, event, data, session):
        assert update_event(event_id=event.id,
                            event=data, db=session) is None

    def test_fields_types_invalid(self, event, session):
        data = {"start": "20.01.2020"}
        with pytest.raises(HTTPException):
            response = update_event(event_id=event.id, event=data, db=session)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_not_is_change_dates_allowed(self, event):
        data = {"start": "20.01.2020"}
        assert is_change_dates_allowed(event, data) is False

    def test_successful_update(self, event, session):
        data = {
            "title": "successful",
            "start": datetime(2021, 1, 20),
            "end": datetime(2021, 1, 21),
        }
        assert isinstance(update_event(1, data, session), Event)
        assert "successful" in update_event(
            event_id=event.id, event=data, db=session).title

    def test_update_db_close(self, event):
        data = {"title": "Problem connecting to db", }
        assert update_event(event_id=event.id,
                            event=data, db=None) is None

    def test_update_event_does_not_exist(self, event, session):
        data = {
            "content": "An update test for an event does not exist"
        }
        assert update_event(
            event_id=500, event=data, db=session) is None

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'

    def test_successful_deletion(self, event_test_client, session, event):
        response = event_test_client.delete("/event/1")
        assert response.ok
        assert by_id(db=session, event_id=1) is None

    def test_delete_failed(self, event_test_client, event):
        response = event_test_client.delete("/event/2")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_no_connection_to_db(self, event):
        with pytest.raises(HTTPException):
            response = delete_event(event_id=1, db=None)
            assert response.status_code == status.\
                HTTP_500_INTERNAL_SERVER_ERROR
