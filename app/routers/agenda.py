from collections import defaultdict 
from datetime import date, timedelta
from typing import Optional, Tuple

from app.dependencies import get_db
from app.internal import agenda_events

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def calc_dates_range_for_agenda(
    start: Optional[date],
    end: Optional[date],
    days: Optional[int]) -> Tuple[date, date]:
    """Create start and end dates eccording to the parameters in the page."""
    if days is not None:
        start = date.today()
        end = start + timedelta(days=days)
    elif start is None or end is None:
        start = date.today()
        end = date.today()
    return start, end


@router.get("/agenda")
def agenda(
    request: Request,
    db: Session = Depends(get_db),
    start_date: Optional[date]=None,
    end_date: Optional[date]=None,
    days: Optional[int]=None) -> Jinja2Templates:
    """Route for the agenda page, using dates range or exact amount of days."""
    
    user_id = 1   # there is no user session yet, so I use user id- 1.
    start_date, end_date = calc_dates_range_for_agenda(start_date, end_date, days)

    events_objects = agenda_events.get_events_per_dates(db, user_id, start_date, end_date)
    events = defaultdict(list)
    for event_object in events_objects:
        event_duration = agenda_events.get_time_delta_string(event_object.start, event_object.end)
        events[event_object.start.date()].append((event_object, event_duration))

    return templates.TemplateResponse("agenda.html", {
        "request": request,
        "events": events, 
        "start_date": start_date,
        "end_date": end_date
    })
