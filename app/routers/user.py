from typing import List
from pydantic import BaseModel, Field

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, UserEvent, Event
from app.internal.utils import save
from fastapi import APIRouter, Depends

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


@router.get("/get_all_users")
async def get_all_users(session=Depends(get_db)):
    return session.query(User).all()


@router.get("/get_user")
async def get_user(user_id: int, session=Depends(get_db)):
    return session.query(User).filter_by(id=user_id).first()


@router.post("/create_user")
def manually_create_user(user: UserModel, session=Depends(get_db)):
    create_user(**user.dict(), session=session)
    return f'User {user.username} successfully created'


def create_user(username: str,
                password: str,
                email: str,
                language: str,
                language_id: int,
                session: Session) -> User:
    """Creates and saves a new user."""

    user = User(
        username=username,
        password=password,
        email=email,
        language=language,
        language_id=language_id
    )
    save(user, session=session)
    return user


def get_users(session: Session, **param):
    """Returns all users filter by param."""

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
