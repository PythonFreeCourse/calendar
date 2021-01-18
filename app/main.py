import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.routers import agenda, invitation
from app.dependencies import STATIC_PATH, TEMPLATES_PATH

app = FastAPI()

app_path = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(app_path, "static")
templates_path = os.path.join(app_path, "templates")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
templates = Jinja2Templates(directory=TEMPLATES_PATH)

app.include_router(agenda.router)
app.include_router(invitation.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcoming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcoming_events,
    })
