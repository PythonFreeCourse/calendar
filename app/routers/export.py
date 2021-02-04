from datetime import datetime, date
from io import BytesIO
from typing import List, Union

import pytz
from fastapi import APIRouter, Depends
from icalendar import Calendar, Event as IcalEvent, vCalAddress, vText
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.config import DOMAIN, ICAL_VERSION, PRODUCT_ID
from app.database.database import get_db
from app.database.models import Event
from app.internal.agenda_events import (
    filter_dates, filter_start_dates, filter_end_dates)
from app.routers.event import get_attendees_email
from app.routers.user import get_all_user_events

router = APIRouter(
    prefix="/export",
    tags=["export"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def export(
        start_date: Union[date, str],  # date or an empty string
        end_date: Union[date, str],
        db: Session = Depends(get_db),
) -> StreamingResponse:
    user_id = 1
    events = get_events_in_time_frame(start_date, end_date, user_id, db)
    file = BytesIO(export_calendar(db, events))
    return StreamingResponse(
        content=file,
        media_type="text/calendar",
        headers={
            # change filename to "pylendar.ics"
            "Content-Disposition": "attachment;filename=pylendar.ics"
        })


def get_events_in_time_frame(
        start_date: Union[date, str],
        end_date: Union[date, str],
        user_id: int, db: Session
) -> List[Event]:
    """Returns all events in a time frame.
    if "start_date" or "end_date" are empty strings,
    it will ignore that parameter when filtering.

    for example:
    if start_date = "" and end_date = datetime.now().date,
    then the function will return all events that ends before end_date."""

    events = get_all_user_events(db, user_id)
    if start_date and end_date:
        filtered_events = filter_dates(
            end=end_date,
            start=start_date,
            events=events
        )
    elif start_date:
        filtered_events = filter_start_dates(
            start=start_date,
            events=events
        )
    elif end_date:
        filtered_events = filter_end_dates(
            end=end_date,
            events=events
        )
    else:
        filtered_events = events

    return filtered_events


def generate_id(event: Event) -> bytes:
    """Creates an unique id."""

    return (
        str(event.id)
        + event.start.strftime('%Y%m%d')
        + event.end.strftime('%Y%m%d')
        + f'@{DOMAIN}'
    ).encode()


def create_ical_calendar():
    """Creates an ical calendar,
    and adds the required information"""

    cal = Calendar()
    cal.add('version', ICAL_VERSION)
    cal.add('prodid', PRODUCT_ID)

    return cal


def add_optional(user_event, data):
    """Adds an optional field if it exists."""

    if user_event.location:
        data.append(('location', user_event.location))

    if user_event.content:
        data.append(('description', user_event.content))

    return data


def create_ical_event(user_event):
    """Creates an ical event,
    and adds the event information"""

    ievent = IcalEvent()
    data = [
        ('organizer', add_attendee(user_event.owner.email, organizer=True)),
        ('uid', generate_id(user_event)),
        ('dtstart', user_event.start),
        ('dtstamp', datetime.now(tz=pytz.utc)),
        ('dtend', user_event.end),
        ('summary', user_event.title),
    ]

    data = add_optional(user_event, data)

    for param in data:
        ievent.add(*param)

    return ievent


def add_attendee(email, organizer=False):
    """Adds an attendee to the event."""

    attendee = vCalAddress(f'MAILTO:{email}')
    if organizer:
        attendee.params['partstat'] = vText('ACCEPTED')
        attendee.params['role'] = vText('CHAIR')
    else:
        attendee.params['partstat'] = vText('NEEDS-ACTION')
        attendee.params['role'] = vText('PARTICIPANT')

    return attendee


def add_attendees(ievent, attendees: list):
    """Adds attendees for the event."""

    for email in attendees:
        ievent.add(
            'attendee',
            add_attendee(email),
            encode=0
        )

    return ievent


def event_to_ical(user_event: Event, attendees: List[str]) -> bytes:
    """Returns an ical event, given an
    "Event" instance and a list of email."""

    ical = create_ical_calendar()
    ievent = create_ical_event(user_event)
    ievent = add_attendees(ievent, attendees)
    ical.add_component(ievent)

    return ical.to_ical()


def export_calendar(session: Session, events: List[Event]) -> bytes:
    """Returns an icalendar, given an list of
    "Event" instances and a list of email."""

    ical = create_ical_calendar()
    for event in events:
        ievent = create_ical_event(event)

        attendees = get_attendees_email(session, event)
        attendees.remove((event.owner.email,))

        ievent = add_attendees(ievent, attendees)
        ical.add_component(ievent)

    return ical.to_ical()
