from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.config import templates
from app.dependencies import get_db
from app.internal.share.share_event import accept
from app.internal.invitation import get_all_invitations, get_invitation_by_id

invitation = APIRouter(
    prefix="/invitations",
    tags=["invitation"],
    dependencies=[Depends(get_db)]
)


@invitation.get("/")
def view_invitations(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("invitations.html", {
        "request": request,
        # recipient_id should be the current user
        # but because we don't have one yet,
        # "get_all_invitations" returns all invitations
        "invitations": get_all_invitations(session=db),
        "message": "Hello, World!"
    })


@invitation.post("/")
async def accept_invitations(invite_id: int = Form(...), db: Session = Depends(get_db)):
    i = get_invitation_by_id(invite_id, session=db)
    accept(i, db)
    return RedirectResponse("/invitations", status_code=HTTP_302_FOUND)
