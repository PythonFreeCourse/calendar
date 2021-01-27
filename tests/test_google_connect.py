from datetime import datetime

import pytest
from app.routers.event import create_event
from app.routers.google_connect import db_cleanup, push_events_to_db


@pytest.fixture
def google_events_mock():
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
                "date": "2021-02-25"
            },
            "end": {
                "date": "2021-02-25"
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
@pytest.mark.usefixtures("google_events_mock")
def test_push_events_to_db(google_events_mock, user, session):
    assert push_events_to_db(google_events_mock, user, session)


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("session")
@pytest.mark.usefixtures("google_events_mock")
def test_clean_up(google_events_mock, user, session):
    for event in google_events_mock:
        print(event)
        location = None
        title = event['summary']
        # support for all day events
        if 'dateTime' in event['start'].keys():
            # part time event
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
        else:
            # all day event
            start = event['start']['date'].split('-')
            start = datetime(
                year=int(start[0]),
                month=int(start[1]),
                day=int(start[2])
            )

            end = event['end']['date'].split('-')
            end = datetime(
                year=int(end[0]),
                month=int(end[1]),
                day=int(end[2])
            )

        if 'location' in event.keys():
            location = event['location']

        create_event(
            db=session,
            title=title,
            start=start,
            end=end,
            owner_id=user.id,
            location=location,
            isGoogleEvent=True
        )

        assert db_cleanup(user, session)
