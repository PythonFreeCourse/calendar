from datetime import datetime as dt
import json
from operator import attrgetter
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from starlette import status
from starlette.responses import RedirectResponse, Response
from starlette.templating import _TemplateResponse

from app.database.models import Comment, Event, User, UserEvent
from app.dependencies import get_db, logger, templates
from app.internal.event import (
    get_invited_emails,
    get_messages,
    get_uninvited_regular_emails,
    raise_if_zoom_link_invalid,
)
from app.internal import comment as cmt
from app.internal.emotion import get_emotion
from app.internal.utils import create_model, get_current_user


EVENT_DATA = Tuple[Event, List[Dict[str, str]], str]
TIME_FORMAT = "%Y-%m-%d %H:%M"
START_FORMAT = "%A, %d/%m/%Y %H:%M"
UPDATE_EVENTS_FIELDS = {
    "title": str,
    "start": dt,
    "end": dt,
    "availability": bool,
    "all_day": bool,
    "is_google_event": bool,
    "content": (str, type(None)),
    "location": (str, type(None)),
    "vc_link": (str, type(None)),
    "category_id": (int, type(None)),
}

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


class EventModel(BaseModel):
    title: str
    start: dt
    end: dt
    content: str
    owner_id: int
    location: str
    is_google_event: bool


@router.get("/")
async def get_events(session=Depends(get_db)):
    return session.query(Event).all()


@router.post("/")
async def create_event_api(event: EventModel, session=Depends(get_db)):
    create_event(
        db=session,
        title=event.title,
        start=event.start,
        end=event.start,
        content=event.content,
        owner_id=event.owner_id,
        location=event.location,
        is_google_event=event.is_google_event,
    )
    return {"success": True}


@router.get("/edit", include_in_schema=False)
@router.get("/edit")
async def eventedit(request: Request) -> Response:
    return templates.TemplateResponse("eventedit.html", {"request": request})


@router.post("/edit", include_in_schema=False)
async def create_new_event(
    request: Request,
    session=Depends(get_db),
) -> Response:
    data = await request.form()
    title = data["title"]
    content = data["description"]
    start = dt.strptime(
        data["start_date"] + " " + data["start_time"],
        TIME_FORMAT,
    )
    end = dt.strptime(data["end_date"] + " " + data["end_time"], TIME_FORMAT)
    owner_id = get_current_user(session).id
    availability = data.get("availability", "True") == "True"
    location = data["location"]
    all_day = data["event_type"] and data["event_type"] == "on"

    vc_link = data["vc_link"]
    category_id = data.get("category_id")
    is_google_event = data.get("is_google_event", "True") == "True"

    invited_emails = get_invited_emails(data["invited"])
    uninvited_contacts = get_uninvited_regular_emails(
        session,
        owner_id,
        title,
        invited_emails,
    )

    if vc_link is not None:
        raise_if_zoom_link_invalid(vc_link)

    event = create_event(
        db=session,
        title=title,
        start=start,
        end=end,
        owner_id=owner_id,
        all_day=all_day,
        content=content,
        location=location,
        vc_link=vc_link,
        invitees=invited_emails,
        category_id=category_id,
        availability=availability,
        is_google_event=is_google_event,
    )

    messages = get_messages(session, event, uninvited_contacts)
    return RedirectResponse(
        router.url_path_for("eventview", event_id=event.id)
        + f'messages={"---".join(messages)}',
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/{event_id}", include_in_schema=False)
async def eventview(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
) -> Response:
    event, comments, end_format = get_event_data(db, event_id)
    start_format = START_FORMAT
    if event.all_day:
        start_format = "%A, %d/%m/%Y"
        end_format = ""
    messages = request.query_params.get("messages", "").split("---")
    return templates.TemplateResponse(
        "eventview.html",
        {
            "request": request,
            "event": event,
            "comments": comments,
            "start_format": start_format,
            "end_format": end_format,
            "messages": messages,
        },
    )


@router.post("/{event_id}/owner")
async def change_owner(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
):
    form = await request.form()
    if "username" not in form:
        return RedirectResponse(
            router.url_path_for("eventview", event_id=event_id),
            status_code=status.HTTP_302_FOUND,
        )
    username = form["username"]
    user = db.query(User).filter_by(username=username).first()
    try:
        user_id = user.id
    except AttributeError as e:
        error_message = f"Username does not exist. {form['username']}"
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )
    owner_to_update = {"owner_id": user_id}
    _update_event(db, event_id, owner_to_update)
    return RedirectResponse(
        router.url_path_for("eventview", event_id=event_id),
        status_code=status.HTTP_302_FOUND,
    )


def by_id(db: Session, event_id: int) -> Event:
    """Get a single event by id"""
    if not isinstance(db, Session):
        error_message = (
            f"Could not connect to database. "
            f"db instance type received: {type(db)}"
        )
        logger.critical(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )

    try:
        event = db.query(Event).filter_by(id=event_id).one()
    except NoResultFound:
        error_message = f"Event ID does not exist. ID: {event_id}"
        logger.exception(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message,
        )
    except MultipleResultsFound:
        error_message = (
            f"Multiple results found when getting event. Expected only one. "
            f"ID: {event_id}"
        )
        logger.critical(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )
    return event


def is_end_date_before_start_date(start_date: dt, end_date: dt) -> bool:
    """Check if the start date is earlier than the end date"""
    return start_date > end_date


def check_change_dates_allowed(old_event: Event, event: Dict[str, Any]):
    allowed = 1
    try:
        start_date = event.get("start", old_event.start)
        end_date = event.get("end", old_event.end)
        if is_end_date_before_start_date(start_date, end_date):
            allowed = 0
    except TypeError:
        allowed = 0
    if allowed == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid times",
        )


def is_fields_types_valid(to_check: Dict[str, Any], types: Dict[str, Any]):
    """validate dictionary values by dictionary of types"""
    errors = []
    for field_name, field_type in to_check.items():
        if types[field_name] and not isinstance(field_type, types[field_name]):
            errors.append(
                f"{field_name} is '{type(field_type).__name__}' and"
                + f"it should be from type '{types[field_name].__name__}'",
            )
            logger.warning(errors)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )


def get_event_with_editable_fields_only(
    event: Dict[str, Any],
) -> Dict[str, Any]:
    """Remove all keys that are not allowed to update"""

    edit_event = {i: event[i] for i in UPDATE_EVENTS_FIELDS if i in event}
    # Convert `availability` value into boolean.
    if "availability" in edit_event.keys():
        edit_event["availability"] = edit_event["availability"] == "True"
    if "is_google_event" in edit_event.keys():
        edit_event["is_google_event"] = edit_event["is_google_event"] == "True"
    return edit_event


def _update_event(db: Session, event_id: int, event_to_update: Dict) -> Event:
    try:
        # Update database
        db.query(Event).filter(Event.id == event_id).update(
            event_to_update,
            synchronize_session=False,
        )

        db.commit()
        return by_id(db, event_id)
    except (AttributeError, SQLAlchemyError) as e:
        logger.exception(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def update_event(event_id: int, event: Dict, db: Session) -> Optional[Event]:
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


def create_event(
    db: Session,
    title: str,
    start,
    end,
    owner_id: int,
    all_day: bool = False,
    content: Optional[str] = None,
    location: Optional[str] = None,
    vc_link: str = None,
    color: Optional[str] = None,
    invitees: List[str] = None,
    category_id: Optional[int] = None,
    availability: bool = True,
    is_google_event: bool = False,
):
    """Creates an event and an association."""

    invitees_concatenated = ",".join(invitees or [])

    event = create_model(
        db,
        Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
        location=location,
        vc_link=vc_link,
        color=color,
        emotion=get_emotion(title, content),
        invitees=invitees_concatenated,
        all_day=all_day,
        category_id=category_id,
        availability=availability,
        is_google_event=is_google_event,
    )
    create_model(db, UserEvent, user_id=owner_id, event_id=event.id)
    return event


def sort_by_date(events: List[Event]) -> List[Event]:
    """Sorts the events by the start of the event."""

    temp = events.copy()
    return sorted(temp, key=attrgetter("start"))


def get_attendees_email(session: Session, event: Event):
    return (
        session.query(User.email)
        .join(UserEvent)
        .filter(UserEvent.events == event)
        .all()
    )


def get_participants_emails_by_event(db: Session, event_id: int) -> List[str]:
    """Returns a list of all the email address of the event invited users,
    by event id."""
    return [
        email[0]
        for email in db.query(User.email)
        .select_from(Event)
        .join(UserEvent, UserEvent.event_id == Event.id)
        .join(User, User.id == UserEvent.user_id)
        .filter(Event.id == event_id)
        .all()
    ]


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
            detail="Deletion failed",
        )


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)) -> Response:
    # TODO: Check if the user is the owner of the event.
    event = by_id(db, event_id)
    participants = get_participants_emails_by_event(db, event_id)
    _delete_event(db, event)
    if participants and event.start > dt.now():
        pass
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(url="/calendar", status_code=status.HTTP_200_OK)


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

    if not is_date_before(values["start"], values["end"]):
        return None
    try:
        new_event = create_model(db, Event, **values)
        create_model(
            db,
            UserEvent,
            user_id=values["owner_id"],
            event_id=new_event.id,
        )
        return new_event
    except (AssertionError, AttributeError, TypeError) as e:
        logger.exception(e)
        return None


def get_template_to_share_event(
    event_id: int,
    user_name: str,
    db: Session,
    request: Request,
) -> _TemplateResponse:
    """Gives shareable template of the event.

    Args:
        event_id: Event to share
        user_name: The user who shares the event
        db: The database to get the event from
        request: The request we got from the user using FastAPI.

    Returns:
        Shareable HTML with data from the database about the event.
    """

    event = by_id(db, event_id)
    msg_info = {"sender_name": user_name, "event": event}
    return templates.TemplateResponse(
        "share_event.html",
        {"request": request, "msg_info": msg_info},
    )


@router.post("/{event_id}")
async def add_comment(
    request: Request,
    event_id: int,
    session: Session = Depends(get_db),
) -> Response:
    """Creates a comment instance in the DB. Redirects back to the event's
    comments tab upon creation."""
    form = await request.form()
    data = {
        "user_id": get_current_user(session).id,
        "event_id": event_id,
        "content": form["comment"],
        "time": dt.now(),
    }
    create_model(session, Comment, **data)
    path = router.url_path_for("view_comments", event_id=str(event_id))
    return RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)


def get_event_data(db: Session, event_id: int) -> EVENT_DATA:
    """Retrieves all data necessary to display the event with the given id.

    Args:
        db (Session): DB session.
        event_id (int): ID of Event to fetch data for.

    Returns:
        tuple(Event, list(dict(str: str)), str):
            Tuple consisting of:
                Event instance,
                list of dictionaries with info for all comments in the event.
                time format for the event's end time.

    Raises:
        None
    """
    event = by_id(db, event_id)
    comments = json.loads(cmt.display_comments(db, event))
    end_format = (
        "%H:%M" if event.start.date() == event.end.date() else START_FORMAT
    )
    return event, comments, end_format


@router.get("/{event_id}/comments")
async def view_comments(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Renders event comment tab view.
    This essentially the same as `eventedit`, only with comments tab auto
    showed."""
    event, comments, end_format = get_event_data(db, event_id)
    return templates.TemplateResponse(
        "eventview.html",
        {
            "request": request,
            "event": event,
            "comments": comments,
            "comment": True,
            "start_format": START_FORMAT,
            "end_format": end_format,
        },
    )


@router.post("/comments/delete")
async def delete_comment(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Deletes a comment instance from the db.

    Redirects back to the event's comments tab upon deletion.
    """
    form = await request.form()
    try:
        comment_id = int(form["comment_id"])
        event_id = int(form["event_id"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment or event id",
        )
    cmt.delete_comment(db, comment_id)
    path = router.url_path_for("view_comments", event_id=str(event_id))
    return RedirectResponse(path, status_code=303)
