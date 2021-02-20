from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import MessageStatusEnum
from app.dependencies import templates, get_db
from app.internal.notification import (
    get_invitation_by_id, get_unread_notifications,
    get_all_messages, get_message_by_id, get_history_notifications
)
from app.internal.utils import get_current_user

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
    """Returns the Notifications page route.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            The Notifications HTML page.
        """
    # TODO: get current user
    user = get_current_user(db)
    return templates.TemplateResponse("new_notification.html", {
        "request": request,
        'new_messages': bool(get_all_messages),
        "notifications": get_unread_notifications(session=db, user_id=user.id),
    })


@router.get("/history")
async def view_old_notifications(
        request: Request,
        db: Session = Depends(get_db),
):
    """Returns the Historical Notifications page route.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            The Historical Notifications HTML page.
        """
    user = get_current_user(db)
    return templates.TemplateResponse("old_notification.html", {
        "request": request,
        "notifications": get_history_notifications(session=db, user_id=user.id),
    })


@router.post("/invitation/accept")
async def accept_invitations(
        request: Request,
        db: Session = Depends(get_db),
):
    """Creates a new connection between the User and the Event in the database.

        See Also:
            models.Invitation.accept for more information.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            A redirect to where the user called the route from.
        """
    data = await request.form()
    invite_id = int(data["invite_id"])

    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.accept(db)

    return RedirectResponse(url=data["next"], status_code=HTTP_302_FOUND)


@router.post("/invitation/decline")
async def decline_invitations(
        request: Request,
        db: Session = Depends(get_db),
):
    """Declines an invitations.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            A redirect to where the user called the route from.
        """
    data = await request.form()
    invite_id = int(data["invite_id"])
    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.decline(db)

    return RedirectResponse(url=data["next"], status_code=HTTP_302_FOUND)


@router.post("/message/read")
async def mark_message_as_read(
        request: Request,
        db: Session = Depends(get_db),
):
    """Marks a message as read.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            A redirect to where the user called the route from.
        """
    data = await request.form()
    message_id = int(data["message_id"])

    message = await get_message_by_id(message_id, session=db)
    if message:
        message.mark_as_read(db)

    return RedirectResponse(url=data["next"], status_code=HTTP_302_FOUND)


@router.post("/message/read/all")
async def mark_all_as_read(
        request: Request,
        db: Session = Depends(get_db)
):
    """Marks all messages as read.

        Args:
            request: The HTTP request.
            db: Optional; The database connection.

        Returns:
            A redirect to where the user called the route from.
        """
    user_id = 1
    data = await request.form()

    for message in get_all_messages(db, user_id):
        if message.status == MessageStatusEnum.UNREAD:
            message.mark_as_read(db)

    return RedirectResponse(url=data["next"], status_code=HTTP_302_FOUND)
