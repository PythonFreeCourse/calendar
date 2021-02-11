from datetime import datetime
import pytest
from loguru import logger

import app.routers.google_connect as google_connect
from app.routers.event import create_event
from app.database.models import OAuthCredentials
from app.routers.user import create_user

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock


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


@pytest.fixture
def credentials():
    cred = Credentials(
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry=datetime(2021, 1, 28)
    )

    return cred


def safe_run_local_server(*args, **kwargs):
    logger.debug('running server')


@pytest.mark.usefixtures("user", "session", "google_events_mock")
def test_push_events_to_db(google_events_mock, user, session):
    assert google_connect.push_events_to_db(google_events_mock, user, session)


@pytest.mark.usefixtures("user", "session", "google_events_mock")
def test_clean_up(google_events_mock, user, session):
    for event in google_events_mock:
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
            is_google_event=True
        )

        assert google_connect.db_cleanup(user, session)


@pytest.mark.usefixtures("session")
def test_get_credentials_from_db(session):
    user = create_user(session=session,
                       username='new_test_username',
                       password='new_test_password',
                       email='new_test.email@gmail.com',
                       language='english',
                       language_id=1)

    credentials = OAuthCredentials(
        owner=user,
        token="somecode",
        refresh_token="somecode",
        token_uri="some_uri",
        client_id="somecode",
        client_secret="some_secret",
        expiry=datetime(2021, 2, 22)
    )
    session.add(credentials)
    session.commit()
    assert user.oauth_credentials is not None
    session.close()
    return_val = google_connect.get_credentials_from_db(user)
    assert return_val[1]


@pytest.mark.usefixtures("session", "user", "credentials")
def test_refresh_token(mocker, session, user, credentials):

    mocker.patch(
        'google.oauth2.credentials.Credentials.refresh',
        return_value=logger.debug('refreshed')
    )

    assert google_connect.refresh_token(credentials, user, session)

    mocker.patch(
        'google.oauth2.credentials.Credentials.expired',
        return_value=False
    )

    assert google_connect.refresh_token(credentials, user, session)


@pytest.mark.usefixtures("session", "user", "credentials")
def test_get_current_year_events(mocker, user, session, credentials):
    class mock_events:
        def __init__(self, service):
            self.service = service

        def list(self, *args):
            request = self.service.events().list(calendarId='primary',
                                                 timeMin=datetime(
                                                     2021, 1, 1).isoformat(),
                                                 timeMax=datetime(
                                                     2022, 1, 1).isoformat(),
                                                 singleEvents=True,
                                                 orderBy='startTime'
                                                 )
            http = HttpMock(
                'calendar-linux.json',
                {'status': '200'}
            )
            response = request.execute(http=http)
            return response

    http = HttpMock(
        './tests/calendar-discovery.json',
        {'status': '200'}
    )

    service = build('calendar', 'v3', http=http)

    mocker.patch(
        'googleapiclient.discovery.build',
        return_value=service,
        events=service
    )
    mocker.patch(
        'googleapiclient.discovery.Resource',
        events=mock_events(service)
    )

    assert google_connect.get_current_year_events(credentials, user, session)


@pytest.mark.usefixtures("session", "google_connect_test_client",
                         "credentials", "google_events_mock")
def test_google_sync(mocker, google_connect_test_client,
                     session, credentials, google_events_mock):
    create_user(session=session,
                username='new_test_username',
                password='new_test_password',
                email='new_test.email@gmail.com',
                language='english',
                language_id=1)

    mocker.patch(
        'app.routers.google_connect.get_credentials_from_db',
        return_value=(credentials, True)
    )
    mocker.patch(
        'app.routers.google_connect.get_current_year_events',
        return_value=google_events_mock
    )
    mocker.patch(
        'app.routers.google_connect.push_events_to_db',
        return_value=True
    )
    mocker.patch(
        'app.routers.google_connect.refresh_token',
        return_value=credentials
    )

    connect = google_connect_test_client.get('/google/sync')
    assert connect.ok


@pytest.mark.usefixtures("user", "session",
                         "google_connect_test_client", "credentials")
def test_google_sync_second_path(mocker, google_connect_test_client,
                                 session, credentials):
    create_user(session=session,
                username='new_test_username',
                password='new_test_password',
                email='new_test.email@gmail.com',
                language='english',
                language_id=1)

    mocker.patch(
        'app.routers.google_connect.get_credentials_from_db',
        return_value=(credentials, False)
    )
    mocker.patch(
        'app.routers.google_connect.is_client_secret_not_none',
        return_value=True
    )
    connect = google_connect_test_client.get('google/sync')
    assert connect.ok


@pytest.mark.usefixtures("session", "google_events_mock",
                         "credentials", "google_connect_test_client")
def test_google_sync_third_path(mocker, google_connect_test_client,
                                session, credentials, google_events_mock):
    create_user(session=session,
                username='new_test_username',
                password='new_test_password',
                email='new_test.email@gmail.com',
                language='english',
                language_id=1)

    mocker.patch(
        'app.routers.google_connect.get_credentials_from_db',
        return_value=(credentials, False)
    )
    mocker.patch(
        'app.routers.google_connect.is_client_secret_not_none',
        return_value=False
    )
    mocker.patch(
        'app.routers.google_connect.get_current_year_events',
        return_value=google_events_mock
    )
    mocker.patch(
        'app.routers.google_connect.push_events_to_db',
        return_value=True
    )
    mocker.patch(
        'google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file',
        return_value=mocker.Mock(name='flow', **{
            "credentials": credentials,
            "run_local_server": safe_run_local_server
        })
    )

    connect = google_connect_test_client.get('google/sync')
    assert connect.ok


def test_is_client_secret_not_none():
    answer = google_connect.is_client_secret_not_none()
    assert answer is not None


@pytest.mark.usefixtures("session")
def test_clean_up_old_credentials_from_db(session):
    google_connect.clean_up_old_credentials_from_db(session)
    assert len(session.query(OAuthCredentials)
               .filter_by(user_id=None).all()) == 0


@pytest.mark.usefixtures("session", 'user', 'credentials')
def test_get_credentials_from_consent_screen(mocker, session,
                                             user, credentials):
    mocker.patch(
        'google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file',
        return_value=mocker.Mock(name='flow', **{
            "credentials": credentials,
            "run_local_server": safe_run_local_server
        })
    )
    assert google_connect.get_credentials_from_consent_screen(
                                                user, session) == credentials


@pytest.mark.usefixtures("session")
def test_get_active_user(session):
    create_user(session=session,
                username='new_test_username',
                password='new_test_password',
                email='new_test.email@gmail.com',
                language='english',
                language_id=1)

    assert google_connect.get_active_user(session=session)


@pytest.mark.usefixtures("session")
def test_create_google_event(session):
    user = create_user(session=session,
                       username='new_test_username',
                       password='new_test_password',
                       email='new_test.email@gmail.com',
                       language='english',
                       language_id=1)

    event = google_connect.create_google_event(
            'title',
            datetime(2021, 1, 1, 15, 15),
            datetime(2021, 1, 1, 15, 30),
            user,
            'location',
            session
            )

    assert event.title == 'title'
