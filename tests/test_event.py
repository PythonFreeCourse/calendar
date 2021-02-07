from app.internal.utils import delete_instance
from datetime import datetime

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from starlette import status

from app.database.models import Comment, Event
from app.routers.event import get_event_data, router
from app.routers.event import (_delete_event, by_id, delete_event,
                               check_change_dates_allowed, update_event,
                               _update_event)

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

NONE_UPDATE_OPTIONS = [
    {}, {"test": "test"},
]

INVALID_FIELD_UPDATE = [
    {"start": "20.01.2020"},
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
    assert response.status_code == status.HTTP_302_FOUND
    assert (client.app.url_path_for('eventview', event_id=1).strip('1')
            in response.headers['location'])


def test_eventedit_post_wrong(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=WRONG_EVENT_FORM_DATA)
    assert response.json()['detail'] == 'VC type with no valid zoom link'


@pytest.mark.parametrize("data", NONE_UPDATE_OPTIONS)
def test_invalid_update(event, data, session):
    assert update_event(event_id=event.id,
                        event=data, db=session) is None


@pytest.mark.parametrize("data", INVALID_FIELD_UPDATE)
def test_invalid_fields(event, data, session):
    with pytest.raises(HTTPException):
        response = update_event(event_id=event.id, event=data, db=session)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_not_check_change_dates_allowed(event):
    data = {"start": "20.01.2020"}
    with pytest.raises(HTTPException):
        assert (
            check_change_dates_allowed(event, data).status_code ==
            status.HTTP_400_BAD_REQUEST
        )


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
    data = {"title": "Problem connecting to db in func update_event", }
    with pytest.raises(HTTPException):
        assert (
            update_event(event_id=event.id, event=data, db=None).status_code ==
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_update_event_does_not_exist(event, session):
    data = {
        "content": "An update test for an event does not exist"
    }
    with pytest.raises(HTTPException):
        response = update_event(event_id=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                event=data, db=session)
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_db_close_update(session, event):
    data = {"title": "Problem connecting to db in func _update_event", }
    with pytest.raises(HTTPException):
        assert (
            _update_event(
                event_id=event.id,
                event_to_update=data,
                db=None).status_code ==
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_repr(event):
    assert event.__repr__() == f'<Event {event.id}>'


def test_no_connection_to_db_in_delete(event):
    with pytest.raises(HTTPException):
        response = delete_event(event_id=1, db=None)
        assert (
            response.status_code ==
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_no_connection_to_db_in_internal_deletion(event):
    with pytest.raises(HTTPException):
        assert (
            _delete_event(event=event, db=None).status_code ==
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_successful_deletion(event_test_client, session, event):
    response = event_test_client.delete("/event/1")
    assert response.ok
    with pytest.raises(HTTPException):
        assert "Event ID does not exist. ID: 1" in by_id(
            db=session, event_id=1).content


def test_deleting_an_event_does_not_exist(event_test_client, event):
    response = event_test_client.delete("/event/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_comment(event_test_client: TestClient, session: Session,
                     event: Event) -> None:
    assert session.query(Comment).first() is None
    content = 'test comment'
    path = router.url_path_for('add_comment', event_id=event.id)
    data = {'comment': content}
    response = event_test_client.post(path, data=data, allow_redirects=True)
    assert response.status_code == status.HTTP_200_OK
    assert content in response.text
    comment = session.query(Comment).first()
    assert comment
    delete_instance(session, comment)


def test_get_event_data(session: Session, event: Event,
                        comment: Comment) -> None:
    data = (
        event,
        [{
            'id': 1,
            'avatar': 'profile.png',
            'username': 'test_username',
            'time': '01/01/0001 00:01',
            'content': 'test comment',
        }],
        '%H:%M'
    )
    assert get_event_data(session, event.id) == data


def test_view_comments(event_test_client: TestClient, event: Event,
                       comment: Comment) -> None:
    path = router.url_path_for('view_comments', event_id=event.id)
    response = event_test_client.get(path)
    assert response.status_code == status.HTTP_200_OK
    assert comment.content in response.text


def test_delete_comment(event_test_client: TestClient, session: Session,
                        event: Event, comment: Comment) -> None:
    assert session.query(Comment).first()
    path = router.url_path_for('delete_comment', event_id=event.id,
                               comment_id=comment.id)
    response = event_test_client.get(path)
    assert response.status_code == status.HTTP_200_OK
    assert session.query(Comment).first() is None
