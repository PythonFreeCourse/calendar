from app.internal import crud
from app.database import schemas

user_details = {
    'username': 'username', 'full_name': 'full_name',
    'password': 'password', 'confirm_password': 'password',
    'email': 'example@email.com', 'description': ""}
user = schemas.UserCreate(**user_details)


user_details = {
        'username': 'username', 'full_name': 'full_name',
        'password': 'password', 'confirm_password': 'password',
        'email': 'example@email.com', 'description': ""}


def test_create_user(session):
    user = schemas.UserCreate(**user_details)
    user = crud.create_user(db=session, user=user)
    assert user.username == 'username'


def test_get_user_by_id(session):
    user = schemas.UserCreate(**user_details)
    user = crud.create_user(db=session, user=user)
    user = crud.get_user_by_id(session, 1)
    assert user.username == 'username'


def test_get_user_by_username(session):
    user = schemas.UserCreate(**user_details)
    user = crud.create_user(db=session, user=user)
    user = crud.get_user_by_username(session, 'username')
    assert user.full_name == 'full_name'


def test_get_user_by_email(session):
    user = schemas.UserCreate(**user_details)
    user = crud.create_user(db=session, user=user)
    user = crud.get_user_by_email(session, 'example@email.com')
    assert user.full_name == 'full_name'


def test_delete_user_by_email(session):
    user = schemas.UserCreate(**user_details)
    crud.create_user(db=session, user=user)
    crud.delete_user_by_mail(session, 'example@email.com')
    user = crud.get_user_by_email(session, 'example@email.com')
    assert user is None
