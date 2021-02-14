from operator import attrgetter
from typing import List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import Invitation, Message
from app.dependencies import templates, get_db
from app.internal.utils import mark_as_read, create_model
from app.routers.share import accept, decline

NOTIFICATION_TYPE = Union[Invitation, Message]


router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    dependencies=[Depends(get_db)]
)


@router.get("/")
async def view_notifications(request: Request, db: Session = Depends(get_db)):
    user_id = 1
    return templates.TemplateResponse("notification.html", {
        "request": request,
        "notifications": get_unread_notifications(session=db, user_id=user_id),
    })


@router.post("/accept_invitations")
async def accept_invitations(
        request: Request,
        db: Session = Depends(get_db)
):
    data = await request.form()
    invite_id = list(data.values())[0]

    invitation = get_invitation_by_id(invite_id, session=db)
    accept(invitation, db)

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
    decline(invitation, db)

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
    mark_as_read(db, message)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/mark_all_as_read")
async def mark_all_as_read(
    db: Session = Depends(get_db)
):
    user_id = 1
    for m in get_all_messages(db, user_id):
        if m.status == 'unread':
            mark_as_read(db, m)

    url = router.url_path_for("view_notifications")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


async def get_message_by_id(
        message_id: int, session: Session
) -> Union[Message, None]:
    """Returns a invitation by an id.
    if id does not exist, returns None."""
    return session.query(Message).filter_by(id=message_id).one()


def get_unread_notifications(session: Session, user_id: int):
    return list(filter(
        lambda x: x.status == 'unread',
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
) -> None:
    """Creates a new message."""
    create_model(
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
        invitations = list(session.query(Invitation).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return invitations


def get_invitation_by_id(
        invitation_id: int, session: Session
) -> Union[Invitation, None]:
    """Returns a invitation by an id.
    if id does not exist, returns None."""
    return session.query(Invitation).filter_by(id=invitation_id).first()
