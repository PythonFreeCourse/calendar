import logging
import re

from email_validator import validate_email, EmailSyntaxError
from fastapi import HTTPException

from starlette.status import HTTP_400_BAD_REQUEST

from app.database.models import Event

ZOOM_REGEX = re.compile(r'https://.*?\.zoom.us/[a-z]/.[^.,\b\s]+')


def raise_if_zoom_link_invalid(location):
    if ZOOM_REGEX.search(location) is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="VC type with no valid zoom link")


def get_invited_emails(invited_from_form):
    invited_emails = []
    for invited_email in invited_from_form.split(','):
        invited_email = invited_email.strip()
        try:
            validate_email(invited_email, check_deliverability=False)
            invited_emails.append(invited_email)
        except EmailSyntaxError:
            logging.error(f'{invited_email} is not a valid email address')

    return invited_emails


def get_uninvited_regular_emails(session, owner_id, title, invited_emails):
    regular_invitees = set()
    invitees_query = session.query(Event).with_entities(Event.invitees)
    similar_events_invitees = invitees_query.filter(Event.owner_id == owner_id,
                                                    Event.title == title).all()
    for record in similar_events_invitees:
        regular_invitees.update(record[0].split(','))

    return regular_invitees - set(invited_emails)
