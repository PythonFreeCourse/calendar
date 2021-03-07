from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.internal.security.ouath2 import get_hashed_password
from app.internal.utils import save


def get_by_id(db: Session, user_id: int) -> models.User:
    """query database for a user by unique id"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_by_username(db: Session, username: str) -> models.User:
    """query database for a user by unique username"""
    return (
        db.query(models.User).filter(models.User.username == username).first()
    )


def get_by_mail(db: Session, email: str) -> models.User:
    """query database for a user by unique email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create(db: Session, user: schemas.UserCreate) -> models.User:
    """
    creating a new User object in the database, with hashed password
    """
    unhashed_password = user.password.encode("utf-8")
    hashed_password = get_hashed_password(unhashed_password)
    user_details = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "description": user.description,
    }
    db_user = models.User(**user_details)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_by_mail(db: Session, email: str) -> None:
    """deletes a user from database by unique email"""
    db_user = get_by_mail(db=db, email=email)
    db.delete(db_user)
    db.commit()


def get_users(session: Session, **param):
    """Returns all users filtered by param."""
    try:
        users = list(session.query(models.User).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return users


def does_user_exist(
    session: Session, *, user_id=None, username=None, email=None
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


def get_all_user_events(session: Session, user_id: int) -> List[models.Event]:
    """Returns all events that the user participants in."""
    return (
        session.query(models.Event)
        .join(models.UserEvent)
        .filter(models.UserEvent.user_id == user_id)
        .all()
    )


def _create_user(session, **kw) -> models.User:
    """Creates and saves a new user."""
    user = models.User(**kw)
    save(session, user)
    return user


async def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    creating a new User object in the database, with hashed password
    """
    unhashed_password = user.password.encode("utf-8")
    hashed_password = get_hashed_password(unhashed_password)
    user_details = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "description": user.description,
        "language_id": user.language_id,
        "target_weight": user.target_weight,
    }
    return _create_user(**user_details, session=db)


async def check_unique_fields(
    db: Session,
    new_user: schemas.UserCreate,
) -> dict:
    """Verifying new user details are unique. Return relevant errors"""
    errors = {}
    if db.query(
        db.query(models.User)
        .filter(models.User.username == new_user.username)
        .exists(),
    ).scalar():
        errors["username"] = "That username is already taken"
    if db.query(
        db.query(models.User)
        .filter(models.User.email == new_user.email)
        .exists(),
    ).scalar():
        errors["email"] = "Email already registered"
    return errors
