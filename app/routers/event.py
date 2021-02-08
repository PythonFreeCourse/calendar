from datetime import datetime
from operator import attrgetter
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from starlette import status
from starlette.responses import RedirectResponse

from app.database.database import get_db
from app.database.models import Event, User, UserEvent
from app.dependencies import templates
from app.internal.event import validate_zoom_link
from app.internal.utils import create_model
from app.routers.user import create_user

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("event/eventedit.html",
                                      {"request": request})


@router.post("/edit")
async def create_new_event(request: Request, session=Depends(get_db)):
    data = await request.form()
    title = data['title']
    content = data['description']
    start = datetime.strptime(data['start_date'] + ' ' + data['start_time'],
                              '%Y-%m-%d %H:%M')
    end = datetime.strptime(data['end_date'] + ' ' + data['end_time'],
                            '%Y-%m-%d %H:%M')
    user = session.query(User).filter_by(id=1).first()
    user = user if user else create_user(username="u",
                                         password="p",
                                         email="e@mail.com",
                                         language="",
                                         lanauge_id=1,
                                         session=session)
    owner_id = user.id
    location_type = data['location_type']
    is_zoom = location_type == 'vc_url'
    location = data['location']
    category_id = data.get('category_id')

    if is_zoom:
        validate_zoom_link(location)

    event = create_event(session, title, start, end, owner_id, content,
                         location, category_id=category_id)
    return RedirectResponse(router.url_path_for('eventview',
                                                event_id=event.id),
                            status_code=status.HTTP_302_FOUND)


@router.get("/{event_id}")
async def eventview(request: Request, event_id: int,
                    db: Session = Depends(get_db)):
    event = by_id(db, event_id)
    start_format = '%A, %d/%m/%Y %H:%M'
    end_format = ('%H:%M' if event.start.date() == event.end.date()
                  else start_format)
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event": event,
                                       "start_format": start_format,
                                       "end_format": end_format})


UPDATE_EVENTS_FIELDS = {
    'title': str,
    'start': datetime,
    'end': datetime,
    'content': (str, type(None)),
    'location': (str, type(None)),
    'category_id': (int, type(None))
}


def by_id(db: Session, event_id: int) -> Event:
    """Get a single event by id"""
    if not isinstance(db, Session):
        error_message = (
            f'Could not connect to database. '
            f'db instance type received: {type(db)}')
        logger.critical(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message)

    try:
        event = db.query(Event).filter_by(id=event_id).one()
    except NoResultFound:
        error_message = f"Event ID does not exist. ID: {event_id}"
        logger.exception(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message)
    except MultipleResultsFound:
        error_message = (
            f'Multiple results found when getting event. Expected only one. '
            f'ID: {event_id}')
        logger.critical(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message)
    return event


def is_end_date_before_start_date(
        start_date: datetime, end_date: datetime) -> bool:
    """Check if the start date is earlier than the end date"""

    return start_date > end_date


def check_change_dates_allowed(old_event: Event, event: Dict[str, Any]):
    allowed = 1
    try:
        start_date = event.get('start', old_event.start)
        end_date = event.get('end', old_event.end)
        if is_end_date_before_start_date(start_date, end_date):
            allowed = 0
    except TypeError:
        allowed = 0
    if allowed == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid times")


def is_fields_types_valid(to_check: Dict[str, Any], types: Dict[str, Any]):
    """validate dictionary values by dictionary of types"""
    errors = []
    for field_name, field_type in to_check.items():
        if types[field_name] and not isinstance(field_type, types[field_name]):
            errors.append(
                f"{field_name} is '{type(field_type).__name__}' and"
                + f"it should be from type '{types[field_name].__name__}'")
            logger.warning(errors)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=errors)


def get_event_with_editable_fields_only(event: Dict[str, Any]
                                        ) -> Dict[str, Any]:
    """Remove all keys that are not allowed to update"""

    return {i: event[i] for i in UPDATE_EVENTS_FIELDS if i in event}


def _update_event(db: Session, event_id: int, event_to_update: Dict) -> Event:
    try:
        # Update database
        db.query(Event).filter(Event.id == event_id).update(
            event_to_update, synchronize_session=False)

        db.commit()
        return by_id(db, event_id)
    except (AttributeError, SQLAlchemyError) as e:
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error")


def update_event(event_id: int, event: Dict, db: Session
                 ) -> Optional[Event]:
    # TODO Check if the user is the owner of the event.
    old_event = by_id(db, event_id)
    event_to_update = get_event_with_editable_fields_only(event)
    is_fields_types_valid(event_to_update, UPDATE_EVENTS_FIELDS)
    check_change_dates_allowed(old_event, event_to_update)
    if not event_to_update:
        return None
    event_updated = _update_event(db, event_id, event_to_update)
    # TODO: Send emails to recipients.
    return event_updated


def create_event(db: Session, title: str, start, end, owner_id: int,
                 content: str = None,
                 location: str = None,
                 category_id: int = None,
                 is_google_event: bool = False
                 ):
    """Creates an event and an association."""

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
        location=location,
        category_id=category_id,
        is_google_event=is_google_event
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


def _delete_event(db: Session, event: Event):
    try:
        # Delete event
        db.delete(event)

        # Delete user_event
        db.query(UserEvent).filter(UserEvent.event_id == event.id).delete()

        db.commit()

    except (SQLAlchemyError, AttributeError) as e:
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deletion failed")


@router.delete("/{event_id}")
def delete_event(event_id: int,
                 db: Session = Depends(get_db)):
    # TODO: Check if the user is the owner of the event.
    event = by_id(db, event_id)
    participants = get_participants_emails_by_event(db, event_id)
    _delete_event(db, event)
    if participants and event.start > datetime.now():
        pass
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url="/calendar", status_code=status.HTTP_200_OK)
