from operator import attrgetter
from typing import List
from datetime import datetime
from fastapi import APIRouter, Request, Depends

from app.database.models import Event, Invitation, User
from app.database.models import UserEvent
from app.dependencies import templates
from app.internal.utils import create_model
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from starlette.status import HTTP_302_FOUND



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

def get_event_by_id(db: Session, event_id: int) -> Event:
    """Select event by id"""
    event = db.query(Event).filter(Event.id == event_id).first()
    return event


@router.post('/view/{id}')
async def delete_event(request: Request, event_id: int=id, db: Session = Depends(get_db)):
    # TODO: Check if the user is the owner of the event.
    event = get_event_by_id(db, event_id)
    # TODO do: Check who the guests at the event are.
    # participants = db.query(User.email).join(Invitation).filter_by(event_id=event_id).all()
    try:
        await db.delete(event)
        db.commit()
        if event.start > datetime.now(): # and invited
            pass
            # TODO: Send them a cancellation notice if the deletion is successful
    except SQLAlchemyError:
        return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": event_id})
    return templates.TemplateResponse("/calendar.html",
                                      {"request": request}, status_code=HTTP_302_FOUND)