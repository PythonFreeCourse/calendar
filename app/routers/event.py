from datetime import datetime
from operator import attrgetter
from typing import Any, Dict, List, Optional

from app.database.database import get_db
from app.database.models import Event, User, UserEvent
from app.dependencies import templates
from app.internal.utils import create_model
from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

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


UPDATE_EVENTS_FIELDS = {
    'title': str,
    'start': datetime,
    'end': datetime,
    'content': (str, type(None)),
    'location': (str, type(None))
}


def by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""

    return db.query(Event).filter(Event.id == event_id).first()


def is_date_before(start_date: datetime, end_date: datetime) -> bool:
    """Check if the start date is earlier than the end date"""

    return start_date < end_date


def is_change_dates_allowed(
        db: Session, old_event: Event, event: Dict[str, Any]) -> bool:
    return is_date_before(
        event.get('start', old_event.start),
        event.get('end', old_event.end))


def is_fields_types_valid(to_check: Dict[str, Any], types: Dict[str, Any]
                          ) -> bool:
    """validate dictionary values by dictionary of types"""
    for key in to_check.keys():
        if types[key] and not isinstance(to_check[key], types[key]):
            # for future log
            # print(key, 'is "'+type(to_check[key]).__name__+
            #    '" and it should be from type "'+ types[key].__name__+ '"')
            return False
    return True


def get_event_with_editable_fields_only(event: Dict[str, Any]
                                        ) -> Dict[str, Any]:
    """Remove all keys that are not allowed to update"""

    return {i: event[i] for i in UPDATE_EVENTS_FIELDS.keys() if i in event}


def update_event(event_id: int, event: Dict, db: Session
                 ) -> Optional[Event]:

    # TODO Check if the user is the owner of the event.
    event_to_update = get_event_with_editable_fields_only(event)
    if not is_fields_types_valid(event_to_update, UPDATE_EVENTS_FIELDS):
        return None
    try:
        old_event = by_id(db=db, event_id=event_id)

        if (not event_to_update
                or old_event is None
                or not is_change_dates_allowed(
                    db, old_event, event_to_update)):
            return None

        # Update database
        db.query(Event).filter(Event.id == event_id).update(
            event_to_update, synchronize_session=False)
        db.commit()

        # TODO: Send emails to recipients.
        return by_id(db=db, event_id=event_id)
    except (AttributeError, SQLAlchemyError):
        return None


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


def get_participants_emails_by_event(db: Session, event_id: int) -> List[str]:
    """Returns a list of all the email address of the event invited users,
        by event id."""

    return [email[0] for email in db.query(User.email).
            select_from(Event).
            join(UserEvent, UserEvent.event_id == Event.id).
            join(User, User.id == UserEvent.user_id).
            filter(Event.id == event_id).
            all()]


@router.delete("/{event_id}")
def delete_event(request: Request,
                 event_id: int,
                 db: Session = Depends(get_db)):

    # TODO: Check if the user is the owner of the event.
    event = by_id(db, event_id)
    participants = get_participants_emails_by_event(db, event_id)
    try:
        # Delete event
        db.delete(event)

        # Delete user_event
        db.query(UserEvent).filter(UserEvent.event_id == event_id).delete()

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "event/eventview.html", {"request": request, "event_id": event_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if participants and event.start > datetime.now():
        pass
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url="/calendar", status_code=status.HTTP_200_OK)
