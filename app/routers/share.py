from typing import Dict, List

from sqlalchemy.orm import Session

from app.database.models import Event, Invitation, UserEvent
from app.internal.utils import save
from app.internal.export import get_icalendar
from app.routers.user import does_user_exist, get_users


def sort_emails(
        participants: List[str],
        session: Session,
) -> Dict[str, List[str]]:
    """Sorts emails to registered and unregistered users."""

    emails = {'registered': [], 'unregistered': []}  # type: ignore
    for participant in participants:

        if does_user_exist(email=participant, session=session):
            temp: list = emails['registered']
        else:
            temp: list = emails['unregistered']

        temp.append(participant)

    return emails


def send_email_invitation(
        participants: List[str],
        event: Event,
) -> bool:
    """Sends an email with an invitation."""

    ical_invitation = get_icalendar(event, participants)  # noqa: F841
    for _ in participants:
        # TODO: send email
        pass
    return True


def send_in_app_invitation(
        participants: List[str],
        event: Event,
        session: Session
) -> bool:
    """Sends an in-app invitation for registered users."""

    for participant in participants:
        # email is unique
        recipient = get_users(email=participant, session=session)[0]

        if recipient.id != event.owner.id:
            session.add(Invitation(recipient=recipient, event=event))

        else:
            # if user tries to send to themselves.
            return False

    session.commit()
    return True


def accept(invitation: Invitation, session: Session) -> None:
    """Accepts an invitation by creating an
    UserEvent association that represents
    participantship at the event."""

    association = UserEvent(
        user_id=invitation.recipient.id,
        event_id=invitation.event.id
    )
    invitation.status = 'accepted'
    save(session, invitation)
    save(session, association)


def share(event: Event, participants: List[str], session: Session) -> bool:
    """Sends invitations to all event participants."""

    registered, unregistered = (
        sort_emails(participants, session=session).values()
    )
    if send_email_invitation(unregistered, event):
        if send_in_app_invitation(registered, event, session):
            return True
    return False
