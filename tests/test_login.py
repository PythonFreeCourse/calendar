import pytest

from starlette.status import HTTP_302_FOUND

from app.database.models import User
from app.internal.security.ouath2 import create_jwt_token
from app.internal.security.schema import LoginUser


def test_login_route_ok(security_test_client):
    response = security_test_client.get("/login")
    assert response.ok


REGISTER_DETAIL = {
    'username': 'correct_user', 'full_name': 'full_name',
    'password': 'correct_password', 'confirm_password': 'correct_password',
    'email': 'example@email.com', 'description': ""}

LOGIN_WRONG_DETAILS = [
    ('wrong_user', 'wrong_password', b'Please check your credentials'),
    ('correct_user', 'wrong_password', b'Please check your credentials'),
    ('wrong_user', 'correct_password', b'Please check your credentials'),
    ('', 'correct_password', b'Please check your credentials'),
    ('correct_user', '', b'Please check your credentials'),
    ('', '', b'Please check your credentials'),
    ]

LOGIN_DATA = {'username': 'correct_user', 'password': 'correct_password'}
WRONG_LOGIN_DATA = {
    'username': 'incorrect_user', 'password': 'correct_password'}


def test_register_user(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)


@pytest.mark.parametrize(
    "username, password, expected_response", LOGIN_WRONG_DETAILS)
def test_login_fails(
        session, security_test_client, username, password, expected_response):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    data = {'username': username, 'password': password}
    data = security_test_client.post('/login', data=data).content
    assert expected_response in data


def test_login_successfull(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    res = security_test_client.post('/login', data=LOGIN_DATA)
    assert res.status_code == HTTP_302_FOUND


def test_is_logged_in_dependency_with_logged_in_user(
        session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    security_test_client.post('/login', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert res.json() == {"user": True}


def test_is_logged_in_dependency_without_logged_in_user(
        session, security_test_client):
    res = security_test_client.get('/logout')
    res = security_test_client.get('/protected')
    assert b'Please log in' in res.content


def test_is_manager_in_dependency_with_logged_in_regular_user(
        session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    security_test_client.post('/login', data=LOGIN_DATA)
    res = security_test_client.get('/manager')
    assert b"have a permition" in res.content


def test_is_manager_in_dependency_with_logged_in_manager(
        session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    manager = session.query(User).filter(
        User.username == 'correct_user').first()
    manager.is_manager = True
    session.commit()
    security_test_client.post('/login', data=LOGIN_DATA)
    res = security_test_client.get('/manager')
    assert res.json() == {"manager": True}


def test_logout(session, security_test_client):
    res = security_test_client.get('/logout')
    assert b'Login' in res.content


def test_incorrect_secret_key_in_token(session, security_test_client):
    user = LoginUser(**LOGIN_DATA)
    incorrect_token = create_jwt_token(user, jwt_key="wrong secret key")
    security_test_client.post('/register', data=REGISTER_DETAIL)
    url = f"/login?existing_jwt={incorrect_token}"
    security_test_client.post(f'{url}', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert b'Your token is incorrect' in res.content


def test_expired_token(session, security_test_client):
    security_test_client.get('/logout')
    user = LoginUser(**LOGIN_DATA)
    incorrect_token = create_jwt_token(user, jwt_min_exp=-1)
    security_test_client.post('/register', data=REGISTER_DETAIL)
    url = f"/login?existing_jwt={incorrect_token}"
    security_test_client.post(f'{url}', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert b'expired' in res.content


def test_corrupted_token(session, security_test_client):
    user = LoginUser(**LOGIN_DATA)
    incorrect_token = create_jwt_token(user) + "s"
    security_test_client.post('/register', data=REGISTER_DETAIL)
    url = f"/login?existing_jwt={incorrect_token}"
    security_test_client.post(f'{url}', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert b'Your token is incorrect' in res.content
