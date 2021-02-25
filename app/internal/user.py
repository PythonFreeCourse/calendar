from app.database import models, schemas
from app.internal.security.ouath2 import get_hashed_password
from sqlalchemy.orm import Session


def get_by_id(db: Session, user_id: int) -> models.User:
    """query database for a user by unique id"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_by_username(db: Session, username: str) -> models.User:
    """query database for a user by unique username"""
    return db.query(models.User).filter(
        models.User.username == username).first()


def get_by_mail(db: Session, email: str) -> models.User:
    """query database for a user by unique email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create(db: Session, user: schemas.UserCreate) -> models.User:
    """
    creating a new User object in the database, with hashed password
    """
    unhashed_password = user.password.encode('utf-8')
    hashed_password = get_hashed_password(unhashed_password)
    user_details = {
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'password': hashed_password,
        'description': user.description
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
