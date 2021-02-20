from datetime import datetime
from typing import List

from icalendar import Calendar, Event as IEvent, vCalAddress, vText
import pytz
from sqlalchemy.orm import Session

from app.config import DOMAIN, ICAL_VERSION, PRODUCT_ID
from app.database.models import Event
from app.internal.email import verify_email_pattern
from app.routers.event import get_attendees_email


def get_icalendar(event: Event, emails: List[str]) -> bytes:
    """Returns an iCalendar event in bytes.

    Builds an iCalendar event with information from the Event object.
    and a list of emails.

    Args:
        event: The Event.
        emails: A list of emails.

    Returns:
        An iCalendar that can be used as a string for a file.
    """
    icalendar = _create_icalendar()
    ievent = _get_icalendar_event(event, emails)
    icalendar.add_component(ievent)
    return icalendar.to_ical()


def get_icalendar_with_multiple_events(
        session: Session, events: List[Event]
) -> bytes:
    """Returns an iCalendar event in bytes.

    Builds an iCalendar event with information from the Event object.
    and a list of emails.

    Args:
        session: The database connection.
        events: A list of Events.

    Returns:
        An iCalendar that can be used as a string for a file.
    """
    icalendar = _create_icalendar()
    for event in events:
        emails = get_attendees_email(session, event)
        emails.remove((event.owner.email,))
        ievent = _get_icalendar_event(event, emails)
        icalendar.add_component(ievent)

    return icalendar.to_ical()


def _create_icalendar() -> Calendar:
    """Returns an iCalendar."""
    calendar = Calendar()
    calendar.add('version', ICAL_VERSION)
    calendar.add('prodid', PRODUCT_ID)

    return calendar


def _get_icalendar_event(event: Event, emails: List[str]) -> IEvent:
    """Returns an iCalendar event in bytes.

    Builds an iCalendar event with information from the Event object.
    and a list of emails.

    Args:
        event: The Event.
        emails: A list of emails.

    Returns:
        A iCalendar that can be used as a string for a file.
    """
    ievent = _create_icalendar_event(event)
    _add_attendees(ievent, emails)
    return ievent


def _create_icalendar_event(event: Event) -> IEvent:
    """Returns an iCalendar event with event data.

    Args:
        event: The Event to transform into an iCalendar event.

    Returns:
        An iCalendar event.
    """
    data = [
        ('organizer', _get_v_cal_address(event.owner.email, organizer=True)),
        ('uid', _generate_id(event)),
        ('dtstart', event.start),
        ('dtstamp', datetime.now(tz=pytz.utc)),
        ('dtend', event.end),
        ('summary', event.title),
    ]

    if event.location:
        data.append(('location', event.location))

    if event.content:
        data.append(('description', event.content))

    ievent = IEvent()
    for param in data:
        ievent.add(*param)

    return ievent


def _get_v_cal_address(email: str, organizer: bool = False) -> vCalAddress:
    """Returns a vCalAddress for an attendee.

    Args:
        email: The email of the attendee.
        organizer: A flag whether or not the user is the event organizer.

    Returns:
        A vCalAddress object.
    """
    attendee = vCalAddress(f'MAILTO:{email}')
    if organizer:
        attendee.params['partstat'] = vText('ACCEPTED')
        attendee.params['role'] = vText('CHAIR')
    else:
        attendee.params['partstat'] = vText('NEEDS-ACTION')
        attendee.params['role'] = vText('PARTICIPANT')

    return attendee


def _generate_id(event: Event) -> bytes:
    """Generates a unique encoded ID.

    The ID is generated from the Event ID, start and end times
    and the domain name.

    Args:
        event: The Event.

    Returns:
        A unique encoded ID in bytes.
    """
    return (
            str(event.id)
            + event.start.strftime('%Y%m%d')
            + event.end.strftime('%Y%m%d')
            + f'@{DOMAIN}'
    ).encode()


def _add_attendees(ievent: IEvent, emails: List[str]):
    """Adds attendees to the event.

    Args:
        ievent: The iCalendar event.
        emails: A list of attendees emails.
    """
    for email in emails:
        if verify_email_pattern(email):
            ievent.add('attendee', _get_v_cal_address(email), encode=0)
