from operator import attrgetter
from typing import List, Union

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import (
    Invitation,
    Message,
    InvitationStatusEnum,
    MessageStatusEnum,
)
from app.internal.utils import create_model

NOTIFICATION_TYPE = Union[Invitation, Message]

UNREAD = [
    InvitationStatusEnum.UNREAD,
    MessageStatusEnum.UNREAD,
]

HISTORY = [
    InvitationStatusEnum.DECLINED,
    MessageStatusEnum.READ,
]


async def get_message_by_id(
    message_id: int,
    session: Session,
) -> Union[Message, None]:
    """Returns an invitation by an id.
    if id does not exist, returns None."""
    return session.query(Message).filter_by(id=message_id).first()


def _is_unread(notification: NOTIFICATION_TYPE) -> bool:
    """Returns True if notification is unread, False otherwise."""
    return notification.status in UNREAD


def _is_history(notification: NOTIFICATION_TYPE) -> bool:
    """Returns True if notification should be
    in history page, False otherwise.
    """
    return notification.status in HISTORY


def get_unread_notifications(
    session: Session,
    user_id: int,
) -> List[NOTIFICATION_TYPE]:
    """Returns all unread notifications."""
    return list(filter(_is_unread, get_all_notifications(session, user_id)))


def get_history_notifications(
    session: Session,
    user_id: int,
) -> List[NOTIFICATION_TYPE]:
    """Returns all history notifications."""
    return list(filter(_is_history, get_all_notifications(session, user_id)))


def get_all_notifications(
    session: Session,
    user_id: int,
) -> List[NOTIFICATION_TYPE]:
    """Returns all notifications."""
    invitations: List[Invitation] = get_all_invitations(
        session,
        recipient_id=user_id,
    )

    messages: List[Message] = get_all_messages(session, user_id)

    notifications = invitations + messages
    return sort_notifications(notifications)


def sort_notifications(
    notification: List[NOTIFICATION_TYPE],
) -> List[NOTIFICATION_TYPE]:
    """Sorts the notifications by the creation date."""
    return sorted(notification, key=attrgetter("creation"), reverse=True)


def create_message(
    session: Session,
    msg: str,
    recipient_id: int,
    link=None,
) -> Message:
    """Creates a new message."""
    return create_model(
        session,
        Message,
        body=msg,
        recipient_id=recipient_id,
        link=link,
    )


def get_all_messages(session: Session, recipient_id: int) -> List[Message]:
    """Returns all messages."""
    condition = Message.recipient_id == recipient_id
    return session.query(Message).filter(condition).all()


def get_all_invitations(session: Session, **param) -> List[Invitation]:
    """Returns all invitations filter by param."""
    try:
        invitations = session.query(Invitation).filter_by(**param).all()
    except SQLAlchemyError:
        return []
    else:
        return invitations


def get_invitation_by_id(
    invitation_id: int,
    session: Session,
) -> Union[Invitation, None]:
    """Returns an invitation by an id.
    if id does not exist, returns None."""
    return session.query(Invitation).filter_by(id=invitation_id).first()
