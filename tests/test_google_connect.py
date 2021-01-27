import pytest
# from app.routers.google_connect import db_cleanup, push_events_to_db

from tests.conftest import session
from tests.user_fixture import user


@pytest.fixture
def google_events():
    return [
        {
            "kind": "calendar#event",
            "etag": "somecode",
            "id": "somecode",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=somecode",
            "created": "2021-01-13T09:10:02.000Z",
            "updated": "2021-01-13T09:10:02.388Z",
            "summary": "some title",
            "creator": {
                "email": "someemail",
                "self": True
            },
            "organizer": {
                "email": "someemail",
                "self": True
            },
            "start": {
                "dateTime": "2021-02-25T13:00:00+02:00"
            },
            "end": {
                "dateTime": "2021-02-25T14:00:00+02:00"
            },
            "iCalUID": "somecode",
            "sequence": 0,
            "reminders": {
                "useDefault": True
            }
        },
        {
            "kind": "calendar#event",
            "etag": "somecode",
            "id": "somecode",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=somecode",
            "created": "2021-01-13T09:10:02.000Z",
            "updated": "2021-01-13T09:10:02.388Z",
            "summary": "some title to all day event",
            "creator": {
                "email": "someemail",
                "self": True
            },
            "organizer": {
                "email": "someemail",
                "self": True
            },
            "start": {
                "dateTime": "2021-02-25"
            },
            "end": {
                "dateTime": "2021-02-25"
            },
            "iCalUID": "somecode",
            "sequence": 0,
            "reminders": {
                "useDefault": True
            }
        }
    ]


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("session")
@pytest.mark.usefixtures("google_events")
def test_push_events_to_db(session=session, user=user, events=google_events):
    print(session, user, events)
    assert False
