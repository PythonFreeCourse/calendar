from fastapi import Depends, APIRouter, Request
from starlette.responses import RedirectResponse
from loguru import logger

from app.internal.utils import get_current_user
from app.dependencies import get_db
from app.internal.google_connect import get_credentials, fetch_save_events
from app.routers.profile import router as profile

router = APIRouter(
    prefix="/google",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)


@router.get("/sync")
async def google_sync(request: Request,
                      session=Depends(get_db)) -> RedirectResponse:
    '''Sync with Google - if user never synced with google this funcion will take
    the user to a consent screen to use his google calendar data with the app.
    '''

    user = get_current_user(session)  # getting active user

    # getting valid credentials
    credentials = get_credentials(user=user, session=session)

    if credentials is None:
        # in case credentials is none, this is mean there isn't a client_secret
        logger.error("GoogleSync isn't available - missing client_secret.json")

    # fetch and save the events com from Google Calendar
    fetch_save_events(credentials=credentials, user=user, session=session)

    url = profile.url_path_for('profile')
    return RedirectResponse(url=url)
