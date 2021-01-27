from datetime import datetime
from operator import attrgetter

from typing import Dict, List, Optional, Any

from app.database.models import Event, UserEvent
from app.dependencies import templates
from app.internal.utils import create_model
from fastapi import APIRouter, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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


def by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""

    return db.query(Event).filter(Event.id == event_id).first()


def is_date_before(start_date: datetime, end_date: datetime) -> bool:
    """Check if the start date is earlier than the end date"""

    return start_date < end_date


def is_it_possible_to_change_dates(
        db: Session, old_event: Event, event: Dict[str, Any]) -> bool:
    return is_date_before(
        event.get('start', old_event.start),
        event.get('end', old_event.end))


def get_items_that_can_be_updated(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only that keys to update"""

    return {i: event[i] for i in (
        'title', 'start', 'end', 'content', 'location') if i in event}


def update_event(event_id: int, event: Dict, db: Session
                 ) -> Optional[Event]:

    # TODO Check if the user is the owner of the event.

    event_to_update = get_items_that_can_be_updated(event)
    if not event_to_update:
        return None
    try:
        old_event = by_id(db=db, event_id=event_id)
        if old_event is None or not is_it_possible_to_change_dates(
                db, old_event, event_to_update):
            return None

        # Update database
        db.query(Event).filter(Event.id == event_id).update(
            event_to_update, synchronize_session=False)
        db.commit()

        # TODO: Send emails to recipients.
    except (AttributeError, SQLAlchemyError, TypeError):
        return None
    return by_id(db=db, event_id=event_id)


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
