import bcrypt
from database import models, schemas
from sqlalchemy.orm import Session


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = user.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    fake_hashed_password = user.password + "notreallyhashed"
    user_details = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': hashed_password
    }
    db_user = models.User(**user_details)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user_by_mail(db: Session, email: str):
    db_user = get_user_by_email(db=db, email=email)
    db.delete(db_user)
    db.commit()