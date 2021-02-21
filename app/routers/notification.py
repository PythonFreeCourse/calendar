from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session

from app.database.models import MessageStatusEnum
from app.dependencies import templates, get_db
from app.internal.notification import (
    get_invitation_by_id,
    get_unread_notifications,
    get_all_messages,
    get_message_by_id,
    get_history_notifications,
)
from app.internal.security.dependancies import current_user
from app.internal.security.schema import CurrentUser
from app.internal.utils import safe_redirect_response

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    dependencies=[
        Depends(get_db),
        Depends(current_user),
    ],
)


@router.get("/", include_in_schema=False)
async def view_notifications(
    request: Request,
    user: CurrentUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Returns the Notifications page route.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        The Notifications HTML page.
    """
    return templates.TemplateResponse(
        "new_notification.html",
        {
            "request": request,
            "new_messages": bool(get_all_messages),
            "notifications": get_unread_notifications(
                session=db,
                user_id=user.user_id,
            ),
        },
    )


@router.get("/history", include_in_schema=False)
async def view_old_notifications(
    request: Request,
    user: CurrentUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Returns the Historical Notifications page route.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        The Historical Notifications HTML page.
    """
    return templates.TemplateResponse(
        "old_notification.html",
        {
            "request": request,
            "notifications": get_history_notifications(
                session=db,
                user_id=user.user_id,
            ),
        },
    )


@router.post("/invitation/accept")
async def accept_invitations(
    invite_id: int = Form(...),
    next: str = Form(...),
    db: Session = Depends(get_db),
):
    """Creates a new connection between the User and the Event in the database.

    See Also:
        models.Invitation.accept for more information.

    Args:
        invite_id: the id of the invitation.
        next: url to redirect to.
        db: Optional; The database connection.

    Returns:
        A redirect to where the user called the route from.
    """
    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.accept(db)

    return safe_redirect_response(next)


@router.post("/invitation/decline")
async def decline_invitations(
    invite_id: int = Form(...),
    next: str = Form(...),
    db: Session = Depends(get_db),
):
    """Declines an invitations.

    Args:
        invite_id: the id of the invitation.
        db: Optional; The database connection.
        next: url to redirect to.

    Returns:
        A redirect to where the user called the route from.
    """
    invitation = get_invitation_by_id(invite_id, session=db)
    invitation.decline(db)

    return safe_redirect_response(next)


@router.post("/message/read")
async def mark_message_as_read(
    message_id: int = Form(...),
    next: str = Form(...),
    db: Session = Depends(get_db),
):
    """Marks a message as read.

    Args:
        message_id: the id of the message.
        db: Optional; The database connection.
        next: url to redirect to.

    Returns:
        A redirect to where the user called the route from.
    """
    message = await get_message_by_id(message_id, session=db)
    if message:
        message.mark_as_read(db)

    return safe_redirect_response(next)


@router.post("/message/read/all")
async def mark_all_as_read(
    next: str = Form(...),
    user: CurrentUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Marks all messages as read.

    Args:
        next: url to redirect to.
        user: user schema object.
        db: Optional; The database connection.

    Returns:
        A redirect to where the user called the route from.
    """
    for message in get_all_messages(db, user.user_id):
        if message.status == MessageStatusEnum.UNREAD:
            message.mark_as_read(db)

    return safe_redirect_response(next)
