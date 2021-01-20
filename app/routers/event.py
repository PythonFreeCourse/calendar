from datetime import datetime
from typing import Dict, Optional, Set

from app.database.models import Event
from app.dependencies import templates
from fastapi import APIRouter, Request
from sqlalchemy import exc
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("eventedit.html", {"request": request})


def get_event_by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""
    return db.query(Event).filter(Event.id == event_id).first()


def check_validation(start_time: datetime, end_time: datetime) -> bool:
    """Check if the start time is earlier than the end time"""

    if start_time < end_time:
        return True
    return False


def get_column_names_event(db: Session) -> Set:
    result = db.execute("select * from events")
    return {col for col in result.keys()}


def check_date_valitation(old_event: Event, event_update: Event):
    """ Checks if the time change is possible, otherwise returns False"""
    try:
        if not check_validation(event_update.start, event_update.end):
            return False
    except TypeError:
        try:
            if event_update.start and not event_update.end:
                if not check_validation(event_update.start, old_event.end):
                    return False
            elif not check_validation(old_event.start, event_update.end):
                return False
        except TypeError:
            return False
    return True


def update_event(event_id: int, event_items: Dict, db: Session) -> Optional[Event]:
    # To do: Check if the user is the owner of the event.
    if not bool(event_items):
        return None
    event_items.pop('id', None)
    event_items.pop('owner_id', None)

    try:
        old_event = get_event_by_id(db=db, event_id=event_id)
    except AttributeError:  # Problem connecting to db
        return None

    if old_event is None:   # No such event number.
        return None

    column_names = get_column_names_event(db)
    for key in event_items.keys():
        if key not in column_names:
            return None

    update = Event(**event_items)
    if not check_date_valitation(old_event, update):
        return None
    try:
        db.query(Event).filter(Event.id == event_id).update(
            event_items, synchronize_session=False)
        db.commit()
        # To do: Sending emails and reset.
    except (AttributeError, exc.SQLAlchemyError):
        return None
    return get_event_by_id(db=db, event_id=event_id)
