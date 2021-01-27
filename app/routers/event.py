from operator import attrgetter
from typing import List, Optional

from fastapi import APIRouter, Request

from app.database.models import Event
from app.database.models import UserEvent
from app.dependencies import templates
from app.internal.utils import create_model

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("event/eventedit.html",
                                      {"request": request})


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": id})


def create_event(db, title, start, end, owner_id, content=None, location=None):
    """Creates an event and an association."""

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
        location=location,
    )
    create_model(
        db, UserEvent,
        user_id=owner_id,
        event_id=event.id
    )
    return event


def sort_by_date(events: List[Event]) -> List[Event]:
    """Sorts the events by the start of the event."""

    temp = events.copy()
    return sorted(temp, key=attrgetter('start'))


def check_date_validation(start_time, end_time) -> bool:
    """Check if the start_date is smaller then the end_time"""

    try:
        return start_time < end_time
    except TypeError:
        return False


def add_new_event(values: dict, db) -> Optional[Event]:
    """Get User values and the DB Session insert the values
    to the DB and refresh it exception in case that the keys
    in the dict is not match to the fields in the DB
    return the Event Class item"""

    if check_date_validation(values['start'], values['end']):
        try:
                new_event = create_model(
                            db, Event, **values)
                create_model(
                        db, UserEvent,
                        user_id=values['owner_id'],
                        event_id=new_event.id
                    )
                return new_event
        except (AssertionError, AttributeError, TypeError) as e:
            # Need to write into log
            print(e)
            return None
    else:
            return None
