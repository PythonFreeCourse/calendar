from datetime import datetime
from operator import attrgetter
from typing import List

from app.database.database import get_db
from app.database.models import Event, Invitation, User, UserEvent
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


def by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""

    return db.query(Event).filter(Event.id == event_id).first()


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
        if participants and event.start > datetime.now():
            pass
            # TODO: Send them a cancellation notice
            # if the deletion is successful
        return RedirectResponse(
            url="/calendar", status_code=status.HTTP_200_OK)
    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "event/eventview.html", {"request": request, "event_id": event_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
