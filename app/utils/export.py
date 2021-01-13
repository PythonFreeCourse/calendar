from datetime import datetime
from typing import List

from icalendar import Calendar, Event, vCalAddress

from app.config import DOMAIN
from app.database.models import Event as UserEvent
from app.utils.config import ICS_VERSION, PRODUCT_ID


def generate_id(event: UserEvent) -> bytes:
    """Creates an unique id from:
    - event id
    - event start time
    - event end time
    - our domain.
    """

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
    cal.add('version', ICS_VERSION)
    cal.add('prodid', PRODUCT_ID)

    return cal


def create_ical_event(user_event):
    """Creates an ical event,
    and adds the event information"""

    ievent = Event()
    data = [
        ('organizer', vCalAddress(user_event.owner.email)),
        ('uid', generate_id(user_event)),
        ('dtstart', user_event.start),
        ('dtstamp', datetime.now()),
        ('dtend', user_event.end),
        ('summary', user_event.title),
    ]

    for param in data:
        ievent.add(*param)

    return ievent


def add_attendees(ievent, attendees: list):
    """Adds attendees for the event."""

    for attendee in attendees:
        ievent.add(
            'attendee',
            vCalAddress(f'MAILTO:{attendee}'),
            encode=0
        )

    return ievent


def event_to_ical(user_event: UserEvent, attendees: List[str]) -> bytes:
    """Returns an ical event,
    given an "UserEvent" instance
    and a list of email"""

    ical = create_ical_calendar()
    ievent = create_ical_event(user_event)
    ievent = add_attendees(ievent, attendees)
    ical.add_component(ievent)

    return ical.to_ical()
