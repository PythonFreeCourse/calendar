from datetime import datetime
from typing import List, Union

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from app.database.models import Invitation
from app.dependencies import get_db
from app.routers.share import accept
from app.database.models import User, Event
from app.internal.utils import save
from app.routers.share import share
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/invitations",
    tags=["invitation"],
    dependencies=[Depends(get_db)]
)


@router.get("/")
def view_invitations(request: Request, db: Session = Depends(get_db)):
    create_data(db)
    return templates.TemplateResponse("invitations.html", {
        "request": request,
        # recipient_id should be the current user
        # but because we don't have one yet,
        # "get_all_invitations" returns all invitations
        "invitations": get_all_invitations(session=db),
    })


@router.post("/")
async def accept_invitations(invite_id: int = Form(...), db: Session = Depends(get_db)):
    i = get_invitation_by_id(invite_id, session=db)
    accept(i, db)
    return RedirectResponse("/", status_code=HTTP_302_FOUND)


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


def create_data(db):
    user1 = User(username="user1", email="email1@gmail.com", password="123456")
    save(user1, db)
    user2 = User(username="user2", email="email2@gmail.com", password="123456")
    save(user2, db)
    me = User(username="Idan", email="Idan@gmail.com", password="123456")
    save(me, db)
    event1 = Event(title="a very big event",
                   content="content",
                   start=datetime.now(),
                   end=datetime.now(),
                   owner_id=user1.id,
                   owner=user1)
    save(event1, db)
    event2 = Event(title="a very small event",
                   content="content",
                   start=datetime.now(),
                   end=datetime.now(),
                   owner_id=user2.id,
                   owner=user2)
    save(event2, db)
    share(event1, ['Idan@gmail.com'], db)
    share(event2, ['Idan@gmail.com'], db)