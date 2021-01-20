import os

from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import session
from app.database.database import Base, SessionLocal, engine
from app.database.models import Event, User
from app.dependencies import get_db
from app.internal.search import get_results_by_keywords
from app.routers import search


app = FastAPI()
app_path = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(app_path, "static")
templates_path = os.path.join(app_path, "templates")
app.include_router(search.router)
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)


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
        "events": upcoming_events
    })
