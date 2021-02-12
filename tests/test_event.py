from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import Null
from starlette import status

from app.database.models import Event
from app.dependencies import get_db
from app.main import app
from app.routers.event import (_delete_event, _update_event, add_new_event,
                               by_id, check_change_dates_allowed, delete_event,
                               is_date_before, update_event, create_event,
                               can_show_event)


CORRECT_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-01-28',
    'start_time': '12:59',
    'end_date': '2021-01-28',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'https://us02web.zoom.us/j/875384596',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'Public',
    'invited': 'a@a.com,b@b.com'
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
    'privacy': 'Public',
    'invited': 'a@a.com,b@b.com'
}

BAD_EMAILS_FORM_DATA = {
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
    'privacy': 'Public',
    'invited': 'a@a.com,b@b.com,ccc'
}

WEEK_LATER_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-02-04',
    'start_time': '12:59',
    'end_date': '2021-02-04',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'https://us02web.zoom.us/j/875384596',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'Public',
    'invited': 'a@a.com,b@b.com'
}

TWO_WEEKS_LATER_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-02-11',
    'start_time': '12:59',
    'end_date': '2021-02-11',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'https://us02web.zoom.us/j/875384596',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'Public',
    'invited': 'a@a.com,b@b.com'
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
                     event.end, event.color, event.category_id]
    response = event_test_client.get(f"/event/{event_id}")
    assert response.ok
    assert b"View Event" in response.content
    for event_detail in event_details:
        assert str(event_detail).encode('utf-8') in response.content, \
            f'{event_detail} not in view event page'


def test_create_event_with_default_availability(client, user, session):
    """
    Test create event with default availability. (busy)
    """
    data = {
        'title': 'test title',
        'start': datetime.strptime('2021-01-01 15:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-01-02 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/875384596',
        'content': 'content',
        'owner_id': user.id,
    }

    event = create_event(session, **data)
    assert event.availability is True


def test_create_event_with_free_availability(client, user, session):
    """
    Test create event with free availability.
    """
    data = {
        'title': 'test title',
        'start': datetime.strptime('2021-01-01 15:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-01-02 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/875384596',
        'content': 'content',
        'owner_id': user.id,
        'availability': False,
    }

    event = create_event(session, **data)
    assert event.availability is False


def test_eventview_without_id(client):
    response = client.get("/event/view")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_eventedit_missing_old_invites(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=CORRECT_EVENT_FORM_DATA)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    different_invitees_event = CORRECT_EVENT_FORM_DATA.copy()
    different_invitees_event['invited'] = 'c@c.com,d@d.com'
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=different_invitees_event)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    for invitee in CORRECT_EVENT_FORM_DATA["invited"].split(","):
        assert invitee in response.headers['location']


def test_eventedit_bad_emails(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=BAD_EMAILS_FORM_DATA)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    different_invitees_event = CORRECT_EVENT_FORM_DATA.copy()
    different_invitees_event['invited'] = 'c@c.com,d@d.com'
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=different_invitees_event)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    for invitee in CORRECT_EVENT_FORM_DATA["invited"].split(","):
        assert invitee in response.headers['location']
    assert 'ccc' not in response.headers['location']


def test_eventedit_post_correct(client, user):
    """
    Test create new event successfully.
    """
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=CORRECT_EVENT_FORM_DATA)
    assert response.ok
    assert (client.app.url_path_for('eventview', event_id=1).strip('1')
            in response.headers['location'])


def test_create_event_with_category(client, user, category, session):
    """
    Test create event with category successfully.
    """
    data = {**CORRECT_EVENT_FORM_DATA, **{'category_id': category.id}}

    response = client.post(client.app.url_path_for('create_new_event'),
                           data=data)
    assert response.ok
    assert (client.app.url_path_for('eventview', event_id=1).strip('1')
            in response.headers['location'])


def test_eventedit_post_wrong(client, user):
    """
    Test create new event unsuccessfully.
    """
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=WRONG_EVENT_FORM_DATA)
    assert response.json()['detail'] == 'VC type with no valid zoom link'


def test_eventedit_with_pattern(client, user):
    response = client.post(client.app.url_path_for('create_new_event'),
                           data=CORRECT_EVENT_FORM_DATA)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    response = client.post(client.app.url_path_for('create_new_event'),
                           data=WEEK_LATER_EVENT_FORM_DATA)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    assert ('Same event happened 1 weeks before too. ' in
            response.headers['location'].replace('+', ' '))

    response = client.post(client.app.url_path_for('create_new_event'),
                           data=TWO_WEEKS_LATER_EVENT_FORM_DATA)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    assert ('Same event happened 1 weeks before too. ' in
            response.headers['location'].replace('+', ' '))
    assert ('Same event happened 2 weeks before too. ' in
            response.headers['location'].replace('+', ' '))


@pytest.mark.parametrize("data", NONE_UPDATE_OPTIONS)
def test_invalid_update(event, data, session):
    """
    Test update existing event.
    """
    assert update_event(event_id=event.id, event=data, db=session) is None


@pytest.mark.parametrize("data", INVALID_FIELD_UPDATE)
def test_invalid_fields(event, data, session):
    """
    Test update existing event.
    """
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


def test_update_event_availability(event, session):
    """
    Test update event's availability.
    """
    original_availability = event.availability
    data = {
        "availability": not original_availability
    }
    assert original_availability is not update_event(event_id=event.id,
                                                     event=data,
                                                     db=session).availability


def test_successful_update(event, session):
    """
    Test update existing event successfully.
    """
    data = {
        "title": "successful",
        "start": datetime(2021, 1, 20),
        "end": datetime(2021, 1, 21),
        "availability": "False",
    }
    assert isinstance(update_event(1, data, session), Event)
    updated_event = update_event(event_id=event.id, event=data, db=session)
    assert "successful" in updated_event.title
    assert updated_event.availability is False


def test_update_event_with_category(today_event, category, session):
    """
    Test update category for an existing event successfully.
    """
    data = {
        "title": "successful",
        "category_id": category.id,
    }
    updated_event = update_event(event_id=today_event.id, event=data,
                                 db=session)
    assert "successful" in updated_event.title
    assert updated_event.category_id == category.id


def test_update_db_close(event):
    data = {"title": "Problem connecting to db in func update_event", }
    with pytest.raises(HTTPException):
        assert (
                update_event(event_id=event.id, event=data,
                             db=None).status_code ==
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


def test_can_show_event_public(event, session, sender, user):
    assert can_show_event(event, session) == event
    assert can_show_event(event, session, user) == event


def test_can_show_event_hidden(event, session, sender, user):
    event.privacy = 'Hidden'
    assert can_show_event(event, session, user) is None
    assert can_show_event(event, session) == event


def test_can_show_event_private(event, session, sender, user):
    event.privacy = 'Private'
    private_event = can_show_event(event=event, session=session, user=user)
    private_attributes = [
        private_event.title, private_event.location,
        private_event.content, private_event.invitees
    ]
    null_attributes = [
        private_event.color, private_event.emotion,
        private_event.category_id
    ]
    is_private_attributes = [attr == 'Private' for attr in private_attributes]
    is_null_attributes = [attr is Null for attr in null_attributes]
    assert all(is_private_attributes) and all(is_null_attributes)


class TestApp:
    client = TestClient(app)
    date_test_data = [datetime.today() - timedelta(1), datetime.today()]
    event_test_data = {
        'title': "Test Title",
        "location": "Fake City",
        "start": date_test_data[0],
        "end": date_test_data[1],
        "content": "Any Words",
        "owner_id": 123}

    @staticmethod
    def test_get_db():
        assert isinstance(next(get_db()), Session)

    @staticmethod
    def test_session_db():
        assert get_db() is not None

    @staticmethod
    def check_is_date_before():
        start = TestApp.date_test_data[0]
        end = TestApp.date_test_data[1]
        assert is_date_before(start, end)

    @staticmethod
    def test_bad_check_validation():
        assert not is_date_before(
            TestApp.date_test_data[0],
            'bad value'
        )

    @staticmethod
    def test_add_event(session: Session):
        assert add_new_event(TestApp.event_test_data, session) is not None

    @staticmethod
    def test_add_bad_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data['no_colume'] = 'some data'
        assert add_new_event(bad_event_test_data, session) is None

    @staticmethod
    def test_add_bad_times_to_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data['start'] = TestApp.date_test_data[1]
        bad_event_test_data['end'] = TestApp.date_test_data[0]
        assert add_new_event(bad_event_test_data, session) is None
