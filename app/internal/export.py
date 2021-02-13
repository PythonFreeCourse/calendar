from datetime import datetime
from typing import List

import pytz
from icalendar import Calendar, vCalAddress, vText
from icalendar import Event as IcalEvent
from sqlalchemy.orm import Session

from app.config import DOMAIN, ICAL_VERSION, PRODUCT_ID
from app.database.models import Event
from app.internal.email import verify_email_pattern
from app.routers.event import get_attendees_email


def generate_id(event: Event) -> bytes:
    """Creates an unique id."""
    return (
            str(event.id)
            + event.start.strftime('%Y%m%d')
            + event.end.strftime('%Y%m%d')
            + f'@{DOMAIN}'
    ).encode()


def create_ical_calendar():
    """Creates an ical calendar, and adds the required information"""
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
    """Creates an ical event, and adds the event information"""
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


def add_attendees(
        ievent: IcalEvent,
        attendees: List[str],
):
    """Adds attendees for the event."""
    for email in attendees:
        if verify_email_pattern(email):
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
