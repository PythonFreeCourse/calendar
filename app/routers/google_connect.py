import  os
from fastapi import Depends, APIRouter, Request
from starlette.responses import RedirectResponse

from google.auth.transport.requests import Request as google_request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.database.models import User, OAuthCredentials
from app.database.database import get_db
from app.routers.profile import router as profile_router


SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = os.getenv('CLIENT_SECRET')


router = APIRouter(
    prefix="/google",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sync")
async def google_sync(request: Request, session = Depends(get_db)):
    # Get relevant data from database
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
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
        flow.run_local_server( prompt='consent', authorization_prompt_message="")
        credentials = flow.credentials

        oauth_credentials = OAuthCredentials(owner=user, token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret, expiry=credentials.expiry)
        session.add(oauth_credentials)
        session.commit()

    print("clean up db")
    session.query(OAuthCredentials).filter_by(user_id=None).delete()
    session.commit()

    session.close()

    url = profile_router.url_path_for("profile")
    return RedirectResponse(url='/profile')
