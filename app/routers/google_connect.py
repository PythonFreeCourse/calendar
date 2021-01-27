from datetime import datetime
from fastapi import Depends, APIRouter
from starlette.responses import RedirectResponse

from google.auth.transport.requests import Request as google_request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.database.models import Event, User, OAuthCredentials, UserEvent
from app.database.database import get_db, SessionLocal
from app.routers.profile import router as profile_router
from app.config import CLIENT_SECRET_FILE
from app.routers.event import create_event

SCOPES = ['https://www.googleapis.com/auth/calendar']

router = APIRouter(
    prefix="/google",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)


@router.get("/sync")
async def google_sync(session=Depends(get_db)):
    '''Sync with Google - if user never synced with google this funcion will take
    the user to a consent screen to use his google calendar data with the app.
    '''

    # TODO - get connected/current user
    user = session.query(User).filter_by(id=1).first()

    credentials, status = get_credentials_from_db(user, session)
    if not status:
        # first sync
        if CLIENT_SECRET_FILE is None:  # if there is no client_secrets.json
            print('Google Sync is not available - missing client_secret.json')
            url = profile_router.url_path_for("profile")
            return RedirectResponse(url=url)

        print("Fetching new Tokens")
        print(CLIENT_SECRET_FILE)
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRET_FILE,
            scopes=SCOPES
        )

        flow.run_local_server(prompt='consent')
        credentials = flow.credentials

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

    print("clean up db")
    session.query(OAuthCredentials).filter_by(user_id=None).delete()
    session.commit()

    events = get_current_year_events(credentials, user, session)
    push_events_to_db(events, user, session)
    session.close()

    url = profile_router.url_path_for("profile")
    return RedirectResponse(url=url)


def get_current_year_events(
                credentials: Credentials, user: User, session: SessionLocal):
    '''Getting user events from google calendar'''

    service = build('calendar', 'v3', credentials=credentials)

    currrnt_year = datetime.now().year
    start = datetime(currrnt_year, 1, 1).isoformat() + 'Z'
    end = datetime(currrnt_year + 1, 1, 1).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def push_events_to_db(events: list, user: User, session: SessionLocal):
    db_cleanup(user, session)

    for event in events:
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


def db_cleanup(user: User, session: SessionLocal):
    '''removing all user google events so the next time with be syncronized'''

    for user_event in user.events:
        user_event_id = user_event.id
        event = user_event.events
        if event.isGoogleEvent:
            session.query(Event).filter_by(id=event.id).delete()
            session.query(UserEvent).filter_by(id=user_event_id).delete()
            session.commit()


def get_credentials_from_db(user: User, session: SessionLocal):
    '''bring user credential to use with google calendar api
    and save the credential in the db'''

    credentials = None
    status = False

    if user.oauth_credentials is not None:
        print("Loading credentials from DB...")
        db_credentials = user.oauth_credentials
        credentials = Credentials(
            token=db_credentials.token,
            refresh_token=db_credentials.refresh_token,
            token_uri=db_credentials.token_uri,
            client_id=db_credentials.client_id,
            client_secret=db_credentials.client_secret,
            expiry=db_credentials.expiry
        )

        if credentials.expired:
            print('refreshing token')
            credentials.refresh(google_request())
            refreshed_credentials = OAuthCredentials(
                owner=user, token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                expiry=credentials.expiry
            )

            session.add(refreshed_credentials)
            session.commit()

        status = True

    return credentials, status
