from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.database import SessionLocal, engine
from app.database.models import Base
from app.internal.share_event import accept
from app.utils.invitation import get_all_invitations, get_invitation_by_id

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/invitations")
def view_invitations(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("requests.html", {
        "request": request,
        # recipient_id should be the current user
        # but because we don't have one yet,
        # "get_all_invitations" returns all invitations
        "invitations": get_all_invitations(session=db),
        "message": "Hello, World!"
    })


@app.post("/invitations")
async def accept_invitations(
        invite_id: int = Form(...),
        db: Session = Depends(get_db)
):
    invitation = get_invitation_by_id(invite_id, session=db)
    accept(invitation, db)
    return RedirectResponse("/invitations", status_code=HTTP_302_FOUND)


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcoming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcoming_events
    })
