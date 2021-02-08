import logging
import re
from typing import List

from email_validator import validate_email, EmailSyntaxError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from starlette.status import HTTP_400_BAD_REQUEST

from app.database.models import Event

ZOOM_REGEX = re.compile(r'https://.*?\.zoom.us/[a-z]/.[^.,\b\s]+')


def raise_if_zoom_link_invalid(location):
    if ZOOM_REGEX.search(location) is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="VC type with no valid zoom link")


def get_invited_emails(invited_from_form: str):
    invited_emails = []
    for invited_email in invited_from_form.split(','):
        invited_email = invited_email.strip()
        try:
            validate_email(invited_email, check_deliverability=False)
            invited_emails.append(invited_email)
        except EmailSyntaxError:
            logging.error(f'{invited_email} is not a valid email address')

    return invited_emails


def get_uninvited_regular_emails(session: Session,
                                 owner_id: int,
                                 title: str,
                                 invited_emails: List[str]):
    invitees_query = session.query(Event).with_entities(Event.invitees)
    similar_events_invitees = invitees_query.filter(Event.owner_id == owner_id,
                                                    Event.title == title).all()
    all_regular_invitees_concatenated = ''
    for record in similar_events_invitees:
        if record:
            all_regular_invitees_concatenated += ',' + record[0]

    regular_invitees = set(all_regular_invitees_concatenated.split(','))

    return regular_invitees - set(invited_emails)


def check_diffs(checked_event: Event,
                all_events: List[Event]):
    """Returns the repeated events and the week difference"""
    diffs = []
    for event in all_events:
        start_delta = checked_event.start - event.start
        end_delta = checked_event.end - event.end

        # The current event is before the new event and they take the same time
        if start_delta.total_seconds() > 0 and start_delta == end_delta:
            # Difference is in multiple of 7 days
            if start_delta.seconds == 0 and start_delta.days % 7 == 0:
                diffs.append(int(start_delta.days / 7))

    return diffs


def find_pattern(session, event):
    all_events_with_same_name = session.query(Event).filter(
        Event.owner_id == event.owner_id, Event.title == event.title).all()

    return check_diffs(event, all_events_with_same_name)
