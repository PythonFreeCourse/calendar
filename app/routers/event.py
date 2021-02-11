from datetime import datetime as dt
from operator import attrgetter
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from starlette import status
from starlette.responses import RedirectResponse

from app.database.models import Event, User, UserEvent
from app.dependencies import get_db, logger, templates
from app.internal.event import (
    get_invited_emails, get_messages, get_uninvited_regular_emails,
    raise_if_zoom_link_invalid,
)
from app.internal.emotion import get_emotion
from app.internal.utils import create_model
from app.routers.user import create_user

TIME_FORMAT = '%Y-%m-%d %H:%M'

UPDATE_EVENTS_FIELDS = {
    'title': str,
    'start': dt,
    'end': dt,
    'content': (str, type(None)),
    'location': (str, type(None)),
    'category_id': (int, type(None))
}

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
    start = dt.strptime(data['start_date'] + ' ' + data['start_time'],
                        TIME_FORMAT)
    end = dt.strptime(data['end_date'] + ' ' + data['end_time'],
                      TIME_FORMAT)
    user = session.query(User).filter_by(id=1).first()
    user = user if user else create_user(username="u",
                                         password="p",
                                         email="e@mail.com",
                                         language_id=1,
                                         session=session)
    owner_id = user.id
    location_type = data['location_type']
    is_zoom = location_type == 'vc_url'
    location = data['location']
    category_id = data.get('category_id')

    invited_emails = get_invited_emails(data['invited'])
    uninvited_contacts = get_uninvited_regular_emails(session, owner_id,
                                                      title, invited_emails)

    if is_zoom:
        raise_if_zoom_link_invalid(location)

    event = create_event(session, title, start, end, owner_id, content,
                         location, invited_emails, category_id=category_id)

    messages = get_messages(session, event, uninvited_contacts)
    return RedirectResponse(router.url_path_for('eventview', event_id=event.id)
                            + f'messages={"---".join(messages)}',
                            status_code=status.HTTP_302_FOUND)


@router.get("/{event_id}")
async def eventview(request: Request, event_id: int,
                    db: Session = Depends(get_db)):
    event = by_id(db, event_id)
    start_format = '%A, %d/%m/%Y %H:%M'
    end_format = ('%H:%M' if event.start.date() == event.end.date()
                  else start_format)
    messages = request.query_params.get('messages', '').split("---")
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event": event,
                                       "start_format": start_format,
                                       "end_format": end_format,
                                       "messages": messages})


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


def is_end_date_before_start_date(start_date: dt, end_date: dt) -> bool:
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
                 invitees: List[str] = None,
                 is_public: bool = False,
                 category_id: int = None):
    """Creates an event and an association."""

    invitees_concatenated = ','.join(invitees or [])

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
        location=location,
        emotion=get_emotion(title, content),
        invitees=invitees_concatenated,
        is_public=is_public,
        category_id=category_id,
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
    return [email[0] for email in
            db.query(User.email).select_from(Event).join(
                UserEvent, UserEvent.event_id == Event.id).join(
                User, User.id == UserEvent.user_id).filter(
                Event.id == event_id).all()]


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
    if participants and event.start > dt.now():
        pass
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url="/calendar", status_code=status.HTTP_200_OK)


def is_date_before(start_time: dt, end_time: dt) -> bool:
    """Check if the start_date is smaller then the end_time"""
    try:
        return start_time < end_time
    except TypeError:
        return False


def add_new_event(values: dict, db: Session) -> Optional[Event]:
    """Get User values and the DB Session insert the values
    to the DB and refresh it exception in case that the keys
    in the dict is not match to the fields in the DB
    return the Event Class item"""

    if not is_date_before(values['start'], values['end']):
        return None
    try:
        new_event = create_model(db, Event, **values)
        create_model(
            db, UserEvent,
            user_id=values['owner_id'],
            event_id=new_event.id
        )
        return new_event
    except (AssertionError, AttributeError, TypeError) as e:
        logger.exception(e)
        return None


def add_user_to_event(session: Session, user_id: int, event_id: int):
    print(f'inside adding func: event {event_id} user {user_id}')
    user_already_connected = session.query(UserEvent).filter(event_id == event_id, user_id == user_id).one()
    print(user_already_connected)
    if not user_already_connected:
        """ if user is not registered to the event, the system will add him"""
        
        create_model(
            session, UserEvent,
            user_id=user_id,
            event_id=event_id
        )
        return True
    else:
        """if the user has a connection to the event,
        the function will recognize the duplicate and return false."""
        return False