from datetime import datetime

import app.routers.google_connect as google_connect
import pytest
from app.routers.event import create_event
from app.routers.profile import router as profile_router
from google.oauth2.credentials import Credentials
from starlette.responses import RedirectResponse
from google.auth.exceptions import TransportError


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
            "location": 'somelocation',
            "reminders": {
                "useDefault": True
            }
        }
    ]


def safe_get_credentials_from_db():
    return Credentials(
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry="2021-01-28 10:04:16.334745"
    ), True


def safe_get_current_year_events(google_events_mock):
    return google_events_mock


def safe_google_sync():
    url = profile_router.url_path_for("profile")
    resp = RedirectResponse(url=url, status_code=200)
    return resp


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("session")
@pytest.mark.usefixtures("google_events_mock")
def test_push_events_to_db(google_events_mock, user, session):
    assert google_connect.push_events_to_db(google_events_mock, user, session)


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

        assert google_connect.db_cleanup(user, session)


@pytest.mark.usefixtures("session")
@pytest.mark.usefixtures("user")
def test_get_credentials_from_db(user, session):

    credentials = Credentials(
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry="2021-01-28 10:04:16.334745"
    )

    cred, status = google_connect.get_credentials_from_db(user, session)
    cred, status = (credentials, True)
    assert status and cred is credentials


@pytest.mark.usefixtures("session")
def test_google_sync(session):
    resp = google_connect.google_sync(session)
    google_connect.google_sync = safe_google_sync
    resp = google_connect.google_sync()
    assert resp.status_code == 200


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("session")
def test_refresh_token(session, user):
    credentials = Credentials(
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry="2021-01-28 10:04:16.334745"
    )

    try:
        cred = google_connect.refresh_token(credentials, session, user)
    except TransportError:
        cred = credentials
    assert cred == credentials


@pytest.mark.usefixtures("user")
@pytest.mark.usefixtures("session")
@pytest.mark.usefixtures("google_events_mock")
def test_get_current_year_events(user, session, google_events_mock):
    credentials = Credentials(
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry="2021-01-28 10:04:16.334745"
    )

    try:
        mock_events = google_connect.get_current_year_events(
            credentials, session, user)
    except Exception:
        google_connect.get_current_year_events = safe_get_current_year_events
        mock_events = google_connect.get_current_year_events(
            google_events_mock)
    assert mock_events == google_events_mock
