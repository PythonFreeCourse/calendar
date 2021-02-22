from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session

from app.database.models import MessageStatusEnum
from app.dependencies import templates, get_db
from app.internal.notification import (
    get_invitation_by_id,
    get_unread_notifications,
    get_all_messages,
    get_message_by_id,
    get_archived_notifications,
    raise_wrong_id_error,
    is_owner,
)
from app.internal.security.dependancies import current_user, is_logged_in
from app.internal.security.schema import CurrentUser
from app.internal.utils import safe_redirect_response

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    dependencies=[
        Depends(get_db),
        Depends(is_logged_in),
    ],
)


@router.get("/", include_in_schema=False)
async def view_notifications(
    request: Request,
    user: CurrentUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Returns the Notifications page.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        The Notifications HTML page.
    """
    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "new_messages": bool(get_all_messages),
            "notifications": get_unread_notifications(
                session=db,
                user_id=user.user_id,
            ),
        },
    )


@router.get("/archive", include_in_schema=False)
async def view_archive(
    request: Request,
    user: CurrentUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Returns the Archived Notifications page.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        The Archived Notifications HTML page.
    """
    return templates.TemplateResponse(
        "archive.html",
        {
            "request": request,
            "notifications": get_archived_notifications(
                session=db,
                user_id=user.user_id,
            ),
        },
    )


@router.post("/invitation/accept")
async def accept_invitations(
    invite_id: int = Form(...),
    next_url: str = Form(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
):
    """Creates a new connection between the User and the Event in the database.

    See Also:
        models.Invitation.accept for more information.

    Args:
        invite_id: the id of the invitation.
        next_url: url to redirect to.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        A redirect to where the user called the route from.
    """
    invitation = get_invitation_by_id(invite_id, session=db)
    if invitation and is_owner(user, invitation):
        invitation.accept(db)
        return safe_redirect_response(next_url)

    raise_wrong_id_error()


@router.post("/invitation/decline")
async def decline_invitations(
    invite_id: int = Form(...),
    next_url: str = Form(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
):
    """Declines an invitations.

    Args:
        invite_id: the id of the invitation.
        db: Optional; The database connection.
        next_url: url to redirect to.
        user: user schema object.

    Returns:
        A redirect to where the user called the route from.
    """
    invitation = get_invitation_by_id(invite_id, session=db)
    if invitation and is_owner(user, invitation):
        invitation.decline(db)
        return safe_redirect_response(next_url)

    raise_wrong_id_error()


@router.post("/message/read")
async def mark_message_as_read(
    message_id: int = Form(...),
    next_url: str = Form(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
):
    """Marks a message as read.

    Args:
        message_id: the id of the message.
        db: Optional; The database connection.
        next_url: url to redirect to.
        user: user schema object.

    Returns:
        A redirect to where the user called the route from.
    """
    message = await get_message_by_id(message_id, session=db)
    if message and is_owner(user, message):
        message.mark_as_read(db)
        return safe_redirect_response(next_url)

    raise_wrong_id_error()


@router.post("/message/read/all")
async def mark_all_as_read(
    next_url: str = Form(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
):
    """Marks all messages as read.

    Args:
        next_url: url to redirect to.
        user: user schema object.
        db: Optional; The database connection.

    Returns:
        A redirect to where the user called the route from.
    """
    for message in get_all_messages(db, user.user_id):
        if message.status == MessageStatusEnum.UNREAD:
            message.mark_as_read(db)

    return safe_redirect_response(next_url)
