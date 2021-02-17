from operator import attrgetter
from typing import List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import (
    Invitation, Message, InvitationStatusEnum, MessageStatusEnum
)
from app.dependencies import templates, get_db
from app.internal.utils import create_model, get_user

NOTIFICATION_TYPE = Union[Invitation, Message]
UNREAD = [
    InvitationStatusEnum.unread,
    MessageStatusEnum.unread,
]

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    dependencies=[Depends(get_db)]
)


@router.get("/")
async def view_notifications(
        request: Request,
        db: Session = Depends(get_db),
):
    # TODO: get current user
    user = get_user(db, 1)
    return templates.TemplateResponse("notification.html", {
        "request": request,
        'new_messages': bool(get_all_messages),
        "notifications": get_unread_notifications(session=db, user_id=user.id),
    })


@router.post("/accept_invitations")
async def accept_invitations(
        request: Request,
        db: Session = Depends(get_db)
):
    data = await request.form()
    invite_id = list(data.values())[0]

    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.accept(db)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/decline_invitations")
async def decline_invitations(
        request: Request,
        db: Session = Depends(get_db)
):
    data = await request.form()
    invite_id = list(data.values())[0]
    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.decline(db)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/mark_as_read")
async def mark_message_as_read(
        request: Request,
        db: Session = Depends(get_db)
):
    data = await request.form()
    message_id = list(data.values())[0]

    message = await get_message_by_id(message_id, session=db)
    if message:
        message.mark_as_read(db)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/mark_all_as_read")
async def mark_all_as_read(
        db: Session = Depends(get_db)
):
    user_id = 1
    for message in get_all_messages(db, user_id):
        if message.status == 'unread':
            message.mark_as_read(db)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


async def get_message_by_id(
        message_id: int, session: Session
) -> Union[Message, None]:
    """Returns an invitation by an id.
    if id does not exist, returns None."""
    return session.query(Message).filter_by(id=message_id).first()


def is_unread(notification):
    return notification.status in UNREAD


def get_unread_notifications(session: Session, user_id: int):
    return list(filter(
        is_unread,
        get_all_notifications(session, user_id)
    ))


def get_all_notifications(session: Session, user_id: int):
    """Returns all notifications."""
    invitations: List[Invitation] = (
        get_all_invitations(session, recipient_id=user_id))

    messages: List[Message] = (
        get_all_messages(session, user_id))

    notifications: List[NOTIFICATION_TYPE] = invitations + messages

    return sort_notifications(notifications)


def sort_notifications(
        notification: List[NOTIFICATION_TYPE]
) -> List[NOTIFICATION_TYPE]:
    """Sorts the notifications by the creation date."""
    temp = notification.copy()
    return sorted(temp, key=attrgetter('creation'), reverse=True)


def create_message(
        session: Session,
        msg: str,
        recipient_id: int,
        link=None
) -> Message:
    """Creates a new message."""
    return create_model(
        session,
        Message,
        body=msg,
        recipient_id=recipient_id,
        link=link
    )


def get_all_messages(
        session: Session,
        recipient_id: int
) -> List[Message]:
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
        invitation_id: int, session: Session
) -> Union[Invitation, None]:
    """Returns an invitation by an id.
    if id does not exist, returns None."""
    return session.query(Invitation).filter_by(id=invitation_id).first()
