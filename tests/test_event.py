from datetime import datetime

from fastapi import HTTPException
import pytest
from sqlalchemy.orm.exc import NoResultFound
from starlette import status
from starlette.status import HTTP_302_FOUND

from app.database.models import Event
from app.routers.event import get_event_by_id, update_event

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


def test_eventedit(event_test_client):
    response = event_test_client.get("/event/edit")
    assert response.ok
    assert b"Edit Event" in response.content


def test_eventview_with_id(event_test_client, session, event):
    event_id = event.id
    event_details = [event.title, event.content, event.location, event.start,
                     event.end, event.color]
    response = event_test_client.get(f"/event/{event_id}")
    assert response.ok
    assert b"View Event" in response.content
    for event_detail in event_details:
        assert str(event_detail).encode('utf-8') in response.content, \
            f'{event_detail} not in view event page'


def test_eventedit_post_correct(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=CORRECT_EVENT_FORM_DATA)
    assert response.ok
    assert response.status_code == HTTP_302_FOUND
    assert (client.app.url_path_for('eventview', event_id=1).strip('1')
            in response.headers['location'])


def test_eventedit_post_wrong(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=WRONG_EVENT_FORM_DATA)
    assert response.json()['detail'] == 'VC type with no valid zoom link'


@pytest.mark.parametrize("data", INVALID_UPDATE_OPTIONS)
def test_invalid_update(event, data, session):
    assert update_event(event_id=event.id,
                        event=data, db=session) is None


def test_successful_update(event, session):
    data = {
        "title": "successful",
        "start": datetime(2021, 1, 20),
        "end": datetime(2021, 1, 21),
    }
    assert isinstance(update_event(1, data, session), Event)
    assert "successful" in update_event(
        event_id=event.id, event=data, db=session).title


def test_update_db_close(event):
    data = {"title": "Problem connecting to db", }
    with pytest.raises(AttributeError):
        update_event(event_id=event.id, event=data, db=None)


def test_update_event_does_not_exist(event, session):
    data = {
        "content": "An update test for an event does not exist"
    }
    with pytest.raises(HTTPException):
        response = update_event(event_id=500, event=data, db=session)
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_repr(event):
    assert event.__repr__() == f'<Event {event.id}>'


def test_successful_deletion(event_test_client, session, event):
    response = event_test_client.delete("/event/1")
    assert response.ok
    with pytest.raises(NoResultFound):
        get_event_by_id(db=session, event_id=1)


def test_delete_failed(event_test_client, event):
    response = event_test_client.delete("/event/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_event_by_valid_id(session, event):
    event_id = event.id
    result = get_event_by_id(db=session, event_id=event_id)
    expected_type = Event
    assert type(result) == expected_type, \
        f'get_event_by_id returned unexpected type. ' \
        f'Expected: {expected_type}, Actual: {type(result)}'
    assert result.id == event_id, 'get_event_by_id returned the wrong event'


def test_get_event_by_unexisting_id(session):
    event_id = 2
    with pytest.raises(NoResultFound) as excinfo:
        get_event_by_id(db=session, event_id=event_id)
    assert 'Event ID does not exist.' in str(excinfo)
