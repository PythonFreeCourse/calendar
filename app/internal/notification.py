from operator import attrgetter
from typing import Callable, Iterator, List, Union

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_406_NOT_ACCEPTABLE

from app.database.models import (
    Invitation,
    InvitationStatusEnum,
    Message,
    MessageStatusEnum,
)
from app.internal.utils import create_model

WRONG_NOTIFICATION_ID = (
    "The notification id you have entered is wrong\n."
    "If you did not enter the notification id manually, report this exception."
)

NOTIFICATION_TYPE = Union[Invitation, Message]

UNREAD_STATUS = {
    InvitationStatusEnum.UNREAD,
    MessageStatusEnum.UNREAD,
}

ARCHIVED = {
    InvitationStatusEnum.DECLINED,
    MessageStatusEnum.READ,
}


async def get_message_by_id(
    message_id: int,
    session: Session,
) -> Union[Message, None]:
    """Returns an invitation by an id.
    if id does not exist, returns None.
    """
    return session.query(Message).filter_by(id=message_id).first()


def _is_unread(notification: NOTIFICATION_TYPE) -> bool:
    """Returns True if notification is unread, False otherwise."""
    return notification.status in UNREAD_STATUS


def _is_archived(notification: NOTIFICATION_TYPE) -> bool:
    """Returns True if notification should be
    in archived page, False otherwise.
    """
    return notification.status in ARCHIVED


def is_owner(user, notification: NOTIFICATION_TYPE) -> bool:
    """Checks if user is owner of the notification.

    Args:
        notification: a NOTIFICATION_TYPE object.
        user: user schema object.

    Returns:
        True or raises HTTPException.
    """
    if notification.recipient_id == user.user_id:
        return True

    msg = "The notification you are trying to access is not yours."
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail=msg,
    )


def raise_wrong_id_error() -> None:
    """Raises HTTPException.

    Returns:
        None
    """
    raise HTTPException(
        status_code=HTTP_406_NOT_ACCEPTABLE,
        detail=WRONG_NOTIFICATION_ID,
    )


def filter_notifications(
    session: Session,
    user_id: int,
    func: Callable[[NOTIFICATION_TYPE], bool],
) -> Iterator[NOTIFICATION_TYPE]:
    """Filters notifications by "func"."""
    yield from filter(func, get_all_notifications(session, user_id))


def get_unread_notifications(
    session: Session,
    user_id: int,
) -> Iterator[NOTIFICATION_TYPE]:
    """Returns all unread notifications."""
    yield from filter_notifications(session, user_id, _is_unread)


def get_archived_notifications(
    session: Session,
    user_id: int,
) -> List[NOTIFICATION_TYPE]:
    """Returns all archived notifications."""
    yield from filter_notifications(session, user_id, _is_archived)


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
    if id does not exist, returns None.
    """
    return session.query(Invitation).filter_by(id=invitation_id).first()
