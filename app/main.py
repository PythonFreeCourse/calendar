import os

from datetime import date, timedelta
from collections import defaultdict 
from typing import Optional

from app.database.database import engine, SessionLocal
from app.internal import agenda_events

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app_path = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(app_path, "static")
templates_path = os.path.join(app_path, "templates")

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
    upcouming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcouming_events
    })


@app.get("/agenda")
def agenda(
    request: Request,
    start_date: Optional[date]=None,
    end_date: Optional[date]=None,
    days: Optional[int]=None) -> Jinja2Templates:
    """Route for the agenda page, using dates range or exact amount of days."""
    
    user_id = 1   # there is no user session yet, so I use user id- 1.
    start_date, end_date = agenda_events.calc_dates_range_for_agenda(start_date, end_date, days)

    db_session = SessionLocal()
    events_objects = agenda_events.get_events_per_dates(db_session, user_id, start_date, end_date)
    events = defaultdict(list)
    for event_object in events_objects:
        event_duration = agenda_events.get_time_delta_string(event_object.start, event_object.end)
        events[event_object.start.date()].append((event_object, event_duration))
    db_session.close()

    return templates.TemplateResponse("agenda.html", {
        "request": request,
        "events": events, 
        "start_date": start_date,
        "end_date": end_date
    })


