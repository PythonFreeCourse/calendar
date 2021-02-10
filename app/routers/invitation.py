from typing import List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import Invitation
from app.dependencies import get_db, templates
from app.routers.share import accept

router = APIRouter(
    prefix="/invitations",
    tags=["invitation"],
    dependencies=[Depends(get_db)]
)


@router.get("/", include_in_schema=False)
def view_invitations(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("invitations.html", {
        "request": request,
        # TODO: create current user
        # recipient_id should be the current user
        # but because we don't have one yet,
        # "get_all_invitations" returns all invitations
        "invitations": get_all_invitations(session=db),
    })


@router.post("/", include_in_schema=False)
async def accept_invitations(
        request: Request,
        db: Session = Depends(get_db)
):
    data = await request.form()
    invite_id = list(data.values())[0]

    invitation = get_invitation_by_id(invite_id, session=db)
    accept(invitation, db)

    url = router.url_path_for("view_invitations")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/get_all_invitations")
def get_all_invitations(session=Depends(get_db), **param) -> List[Invitation]:
    """Returns all invitations filter by param."""

    try:
        invitations = list(session.query(Invitation).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return invitations


@router.post("/get_invitation_by_id")
def get_invitation_by_id(invitation_id: int,
                         session=Depends(get_db)) -> Union[Invitation, None]:
    """Returns a invitation by an id.
    if id does not exist, returns None."""

    return session.query(Invitation).filter_by(id=invitation_id).first()
