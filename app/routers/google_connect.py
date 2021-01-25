import datetime
import pytz
from fastapi import Depends, APIRouter, Request
from starlette.responses import RedirectResponse

from google.auth.transport.requests import Request as google_request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


from app.database.models import User, OAuthCredentials
from app.database.database import get_db, SessionLocal
from app.routers.profile import router as profile_router
from app.config import CLIENT_SECRET_FILE
from app.routers.event import  create_event
SCOPES = ['https://www.googleapis.com/auth/calendar']


router = APIRouter(
    prefix="/google",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sync")
async def google_sync(request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()

    credentials = None
    if user.oauth_credentials is not None:
        print("Loading credentials from DB...")
        db_credentials = user.oauth_credentials
        credentials = Credentials(token=db_credentials.token, refresh_token=db_credentials.refresh_token, token_uri=db_credentials.token_uri,client_id=db_credentials.client_id, client_secret=db_credentials.client_secret, expiry=db_credentials.expiry)
        
        if credentials.expired:
            print('refreshing token')
            credentials.refresh(google_request())
            refreshed_credentials = OAuthCredentials(owner=user, token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret, expiry=credentials.expiry)
            session.add(refreshed_credentials)
            session.commit()    

    else:
        print("Fetching new Tokens")
        print(CLIENT_SECRET_FILE)
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=CLIENT_SECRET_FILE, scopes=SCOPES)
        flow.run_local_server(prompt='consent')
        credentials = flow.credentials

        oauth_credentials = OAuthCredentials(owner=user, token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret, expiry=credentials.expiry)
        session.add(oauth_credentials)
        session.commit()

    print("clean up db")
    session.query(OAuthCredentials).filter_by(user_id=None).delete()
    session.commit()

    get_current_year_events(credentials, user, session)
    session.close()

    url = profile_router.url_path_for("profile")
    return RedirectResponse(url='/profile')


def get_current_year_events(credentials: Credentials, user: User, session: SessionLocal):
    
    service = build('calendar', 'v3', credentials=credentials)
    
    currrnt_year = datetime.datetime.now().year
    start = datetime.datetime(currrnt_year, 1, 1).isoformat() + 'Z'
    end = datetime.datetime(currrnt_year + 1, 1, 1).isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=start, timeMax=end, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    for event in events:
        location = None
        title = event['summary']
        # support for all day events
        if 'dateTime' in event['start'].keys():
            # part time event
            start = datetime.datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.datetime.fromisoformat(event['end']['dateTime'])
        else:
            # all day event
            start = event['start']['date'].split('-')
            start = datetime.datetime(year=int(start[0]), month=int(start[1]), day=int(start[2]))
            end = event['end']['date'].split('-')
            end = datetime.datetime(year=int(end[0]), month=int(end[1]), day=int(end[2]))
            pass
        
        
        if 'location' in event.keys():
            location = event['location']

        e = create_event(db=session, title=title, start=start, end=end, owner_id=user.id, location=location, isGoogleEvent=True)
    

def db_cleanup():
    pass
