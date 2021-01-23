from datetime import datetime
from operator import attrgetter
from typing import Dict, List, Optional

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


def get_event_by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""
    return db.query(Event).filter(Event.id == event_id).first()


def validate_dates(start_date: datetime, end_date: datetime) -> bool:
    """Check if the start date is earlier than the end date"""
    return start_date < end_date


def update_event(event_id: int, event_dict: Dict, db: Session
                 ) -> Optional[Event]:
    # TODO Check if the user is the owner of the event.

    # Extract only that keys to update
    event_to_update = {i: event_dict[i] for i in (
        'title', 'start', 'end', 'content', 'location') if i in event_dict}
    if not bool(event_to_update):  # Event items is empty
        return None
    try:
        old_event = get_event_by_id(db=db, event_id=event_id)
        if old_event is None or not validate_dates(
                event_to_update.get('start', old_event.start),
                event_to_update.get('end', old_event.end)):
            return None

        db.query(Event).filter(Event.id == event_id).update(
            event_to_update, synchronize_session=False)
        db.commit()
        # TODO: Send emails to recipients.
    except (AttributeError, SQLAlchemyError, TypeError):
        return None
    return get_event_by_id(db=db, event_id=event_id)


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
