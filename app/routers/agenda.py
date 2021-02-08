from collections import defaultdict
from datetime import date, timedelta
import json
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.templating import _TemplateResponse

from app.database.database import get_db
from app.dependencies import templates
from app.internal import agenda_events

router = APIRouter()


def calc_dates_range_for_agenda(
        start: Optional[date],
        end: Optional[date],
        days: Optional[int],
) -> Tuple[date, date]:
    """Create start and end dates according to the parameters in the page."""
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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: Optional[int] = None,
) -> _TemplateResponse:
    """Route for the agenda page, using dates range or exact amount of days."""

    user_id = 1  # there is no user session yet, so I use user id- 1.
    start_date, end_date = calc_dates_range_for_agenda(
        start_date, end_date, days
    )

    events_objects = agenda_events.get_events_per_dates(
        db, user_id, start_date, end_date
    )
    events = defaultdict(list)

    for event_obj in events_objects:
        event_duration = agenda_events.get_time_delta_string(
            event_obj.start, event_obj.end
        )
        events[event_obj.start.date()].append((event_obj, event_duration))
    
    start_date_graph, end_date_graph = calc_dates_range_for_agenda(
        start_date, end_date, 7
        )

    events_objects_for_graph = agenda_events.get_events_per_dates(
        db, user_id, start_date_graph, end_date_graph
        )
    events_for_graph = {str(start_date_graph + timedelta(i)): 0 for i in range(8)}

    for event_obj in events_objects_for_graph:
        events_for_graph[str(event_obj.start.date())] += 1

    return templates.TemplateResponse("agenda.html", {
        "request": request,
        "events": events,
        "events_for_graph": json.dumps(events_for_graph),
        "start_date": start_date,
        "end_date": end_date,
    })
