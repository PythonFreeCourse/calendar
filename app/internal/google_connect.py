from datetime import datetime
from fastapi import Depends

from google.auth.transport.requests import Request as google_request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.database.models import Event, User, OAuthCredentials, UserEvent
from app.dependencies import get_db, SessionLocal
from app.config import CLIENT_SECRET_FILE
from app.routers.event import create_event


SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials(user: User,
                    session: SessionLocal = Depends(get_db)) -> Credentials:
    credentials = get_credentials_from_db(user)

    if credentials is not None:
        credentials = refresh_token(credentials, session, user)
    else:
        credentials = get_credentials_from_consent_screen(
            user=user, session=session)

    return credentials


def fetch_save_events(credentials: Credentials, user: User,
                      session: SessionLocal = Depends(get_db)) -> None:
    if credentials is not None:
        events = get_current_year_events(credentials, user, session)
        push_events_to_db(events, user, session)


def clean_up_old_credentials_from_db(
    session: SessionLocal = Depends(get_db)
) -> None:
    session.query(OAuthCredentials).filter_by(user_id=None).delete()
    session.commit()


def get_credentials_from_consent_screen(user: User,
                                        session: SessionLocal = Depends(get_db)
                                        ) -> Credentials:
    credentials = None

    if not is_client_secret_none():  # if there is no client_secrets.json
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRET_FILE,
            scopes=SCOPES
        )

        flow.run_local_server(prompt='consent')
        credentials = flow.credentials

        push_credentials_to_db(
            credentials=credentials, user=user, session=session
        )

        clean_up_old_credentials_from_db(session=session)

    return credentials


def push_credentials_to_db(credentials: Credentials, user: User,
                           session: SessionLocal = Depends(get_db)
                           ) -> OAuthCredentials:

    oauth_credentials = OAuthCredentials(
        owner=user,
        token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        expiry=credentials.expiry
    )

    session.add(oauth_credentials)
    session.commit()
    return credentials


def is_client_secret_none() -> bool:
    return CLIENT_SECRET_FILE is None


def get_current_year_events(
        credentials: Credentials, user: User,
        session: SessionLocal = Depends(get_db)) -> list:
    '''Getting user events from google calendar'''

    current_year = datetime.now().year
    start = datetime(current_year, 1, 1).isoformat() + 'Z'
    end = datetime(current_year + 1, 1, 1).isoformat() + 'Z'

    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def push_events_to_db(events: list, user: User,
                      session: SessionLocal = Depends(get_db)) -> bool:
    '''Adding google events to db'''
    cleanup_user_google_calendar_events(user, session)

    for event in events:
        # Running over the events that have come from the API
        title = event.get('summary')  # The Google event title

        # support for all day events
        if 'dateTime' in event['start']:
            # This case handles part time events (not all day events)
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
        else:
            # This case handles all day events
            start_in_str = event['start']['date']
            start = datetime.strptime(start_in_str, '%Y-%m-%d')

            end_in_str = event['end']['date']
            end = datetime.strptime(end_in_str, '%Y-%m-%d')

        # if Google Event has a location attached
        location = event.get('location')

        create_google_event(title, start, end, user, location, session)
    return True


def create_google_event(title: str, start: datetime,
                        end: datetime, user: User, location: str,
                        session: SessionLocal = Depends(get_db)) -> Event:
    return create_event(
        # creating an event obj and pushing it into the db
        db=session,
        title=title,
        start=start,
        end=end,
        owner_id=user.id,
        location=location,
        is_google_event=True
    )


def cleanup_user_google_calendar_events(
    user: User, session: SessionLocal = Depends(get_db)
) -> bool:
    '''removing all user google events so the next time will be syncronized'''

    for user_event in user.events:
        user_event_id = user_event.id
        event = user_event.events
        if event.is_google_event:
            session.query(Event).filter_by(id=event.id).delete()
            session.query(UserEvent).filter_by(id=user_event_id).delete()
            session.commit()

    return True


def get_credentials_from_db(user: User) -> Credentials:
    '''bring user credential to use with google calendar api
    and save the credential in the db'''

    credentials = None

    if user.oauth_credentials is not None:
        db_credentials = user.oauth_credentials
        credentials = Credentials(
            token=db_credentials.token,
            refresh_token=db_credentials.refresh_token,
            token_uri=db_credentials.token_uri,
            client_id=db_credentials.client_id,
            client_secret=db_credentials.client_secret,
            expiry=db_credentials.expiry
        )

    return credentials


def refresh_token(credentials: Credentials,
                  user: User, session: SessionLocal = Depends(get_db)
                  ) -> Credentials:

    refreshed_credentials = credentials
    if credentials.expired:
        credentials.refresh(google_request())
        refreshed_credentials = OAuthCredentials(
            owner=user,
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            expiry=credentials.expiry
        )

        session.add(refreshed_credentials)
        session.commit()

    return refreshed_credentials
