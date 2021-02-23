from typing import List

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK

from app.database.models import Event, User, UserEvent
from app.dependencies import get_db
from app.internal.user.availability import disable, enable
from app.internal.utils import get_current_user, save


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


class UserModel(BaseModel):
    username: str
    password: str
    email: str = Field(regex='^\\S+@\\S+\\.\\S+$')
    language: str
    language_id: int


@router.get("/list")
async def get_all_users(session=Depends(get_db)):
    return session.query(User).all()


@router.get("/")
async def get_user(id: int, session=Depends(get_db)):
    return session.query(User).filter_by(id=id).first()


@router.post("/")
def manually_create_user(user: UserModel, session=Depends(get_db)):
    create_user(**user.dict(), session=session)
    return f'User {user.username} successfully created'


def create_user(username: str,
                password: str,
                email: str,
                language_id: int,
                session: Session) -> User:
    """Creates and saves a new user."""

    user = User(
        username=username,
        password=password,
        email=email,
        language_id=language_id
    )
    save(session, user)
    return user


def get_users(session: Session, **param):
    """Returns all users filtered by param."""

    try:
        users = list(session.query(User).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return users


def does_user_exist(
        session: Session,
        *, user_id=None,
        username=None, email=None
):
    """Returns True if user exists, False otherwise.
     function can receive one of the there parameters"""

    if user_id:
        return len(get_users(session=session, id=user_id)) == 1
    if username:
        return len(get_users(session=session, username=username)) == 1
    if email:
        return len(get_users(session=session, email=email)) == 1
    return False


def get_all_user_events(session: Session, user_id: int) -> List[Event]:
    """Returns all events that the user participants in."""

    return (
        session.query(Event).join(UserEvent)
        .filter(UserEvent.user_id == user_id).all()
    )


@router.post("/disable")
def disable_logged_user(
        request: Request, session: Session = Depends(get_db)):
    """route that sends request to disable the user.
    after successful disable it will be directed to main page.
    if the disable fails user will stay at settings page
    and an error will be shown."""
    disable_successful = disable(session, get_current_user)
    if disable_successful:
        # disable succeeded- the user will be directed to homepage.
        url = router.url_path_for("home")
        return RedirectResponse(url=url, status_code=HTTP_200_OK)


@router.post("/enable")
def enable_logged_user(
        request: Request, session: Session = Depends(get_db)):
    """router that sends a request to enable the user.
    if enable successful it will be directed to main page.
    if it fails user will stay at settings page
    and an error will be shown."""
    enable_successful = enable(session, get_current_user)
    if enable_successful:
        # enable succeeded- the user will be directed to homepage.
        url = router.url_path_for("home")
        return RedirectResponse(url=url, status_code=HTTP_200_OK)
