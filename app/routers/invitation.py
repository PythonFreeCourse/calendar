from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Invitation
from app.dependencies import get_db, templates
from app.routers.share import accept

router = APIRouter(
    prefix="/invitations",
    tags=["invitation"],
    dependencies=[Depends(get_db)],
)


@router.get("/", include_in_schema=False)
def view_invitations(
        request: Request, db: Session = Depends(get_db)
) -> Response:
    """Returns the Invitations page route.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.

    Returns:
        The Invitations HTML page.
    """
    return templates.TemplateResponse("invitations.html", {
        "request": request,
        # TODO: Connect to current user.
        #  recipient_id should be the current user
        #  but because we don't have one yet,
        #  "get_all_invitations" returns all invitations
        "invitations": get_all_invitations(db),
    })


@router.post("/", include_in_schema=False)
async def accept_invitations(
        request: Request, db: Session = Depends(get_db)
) -> RedirectResponse:
    """Creates a new connection between the User and the Event in the database.

    See Also:
        share.accept for more information.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.

    Returns:
        An updated Invitations HTML page.
    """
    data = await request.form()
    invite_id = list(data.values())[0]

    invitation = get_invitation_by_id(invite_id, db)
    if invitation:
        accept(invitation, db)

    url = router.url_path_for("view_invitations")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# TODO: should be a get request with the path of:
#  @router.get("/all")
@router.get("/get_all_invitations")
def get_all_invitations(
        db: Session = Depends(get_db), **param: Any
) -> List[Invitation]:
    """Returns all Invitations filtered by the requested parameters.

    Args:
        db: Optional; The database connection.
        **param: A list of parameters to filter by.

    Returns:
        A list of all Invitations.
    """
    try:
        invitations = list(db.query(Invitation).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return invitations


# TODO: should be a get request with the path of:
#  @router.get("/{id}")
@router.post("/get_invitation_by_id")
def get_invitation_by_id(
        invitation_id: int, db: Session = Depends(get_db)
) -> Optional[Invitation]:
    """Returns an Invitation by an ID.

    Args:
        invitation_id: The Invitation ID.
        db: Optional; The database connection.

    Returns:
        An Invitation object if found, otherwise returns None.
    """
    return (db.query(Invitation)
            .filter_by(id=invitation_id)
            .first()
            )
