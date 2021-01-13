from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.status import HTTP_302_FOUND

from app.database.database import Base, engine
from app.features.share_event import accept
from app.utils.invitation import get_all_invitations, get_invitation_by_id


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


<<<<<<< HEAD
@app.get("/invitations")
def view_invitations(request: Request):
    return templates.TemplateResponse("requests.html", {
        "request": request,
        # recipient_id should be the current user
        "invitations": get_all_invitations(),
        "message": "Hello, World!"
    })


@app.post("/invitations")
async def accept_invitations(invite_id: int = Form(...)):
    invitation = get_invitation_by_id(invite_id)
    accept(invitation)
    return RedirectResponse("/invitations", status_code=HTTP_302_FOUND)
=======
@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcouming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcouming_events
    })
>>>>>>> 91696f700debbd35a250ccd6604a77da16d12b30
