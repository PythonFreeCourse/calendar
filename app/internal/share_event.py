from typing import List, Dict, Union

from app.config import session
from app.database.models import Event, Invitation, UserEvent
from app.utils.export import event_to_ical
from app.utils.user import dose_user_exist, get_users
from app.utils.utils import save


def sort_emails(emails: List[str]) -> Dict[str, List[str]]:
    """Sorts emails to registered
    and unregistered users."""

    emails_dict = {'registered': [], 'unregistered': []}  # type: ignore
    for email in emails:

        if dose_user_exist(email=email):
            emails_dict['registered'] += [email]
        else:
            emails_dict['unregistered'] += [email]

    return emails_dict


def send_email_invitation(
        participants: List[str],
        event: Event
):
    """Sends an email with an invitation."""

    ical_invitation = event_to_ical(event, participants)
    for participant in participants:
        # sends an email
        pass


def send_in_app_invitation(
        participants: List[str],
        event: Event
) -> Union[bool, None]:
    """Sends an in-app invitation for registered users."""

    for participant in participants:
        # email is unique
        recipient = get_users(email=participant)[0]

        if recipient.id != event.owner.id:
            session.add(Invitation(recipient=recipient, event=event))

        else:
            # if user tries to send to himself.
            session.rollback()
            return None

    session.commit()
    return True


def accept(invitation: Invitation) -> None:
    """Accepts an invitation by creating an
    UserEvent association that represents
    participantship at the event."""

    association = UserEvent(
        participants=invitation.recipient,
        events=invitation.event
    )
    invitation.status = 'accepted'
    save(invitation)
    save(association)


def share(event: Event, participants: List[str]) -> None:
    """Sends invitations to all event participants."""

    registered, unregistered = sort_emails(participants).values()

    send_in_app_invitation(registered, event)
    send_email_invitation(unregistered, event)
