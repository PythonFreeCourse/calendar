import pytest
from app.internal.security.ouath2 import create_jwt_token, LoginUser
from starlette.status import HTTP_302_FOUND


RESPONSE_OK = 200
REDIRECT_OK = HTTP_302_FOUND


def test_login_route_ok(security_test_client):
    response = security_test_client.get("/login")
    assert response.status_code == RESPONSE_OK


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
    assert res.status_code == REDIRECT_OK


def test_protected_with_logged_in_user(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    security_test_client.post('/login', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert b'correct_user' in res.content


def test_protected_without_logged_in_user(
        session, security_test_client):
    res = security_test_client.get('/protected')
    assert b'Please log in' in res.content


def test_current_user_dependency_exists(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    res = security_test_client.post('/login', data=LOGIN_DATA)
    res = security_test_client.get('/test_user')
    assert b'correct_user' in res.content


def test_logout(session, security_test_client):
    res = security_test_client.get('/logout')
    assert b'Login' in res.content


def test_current_user_dependency_not_exists(
        session, security_test_client):
    res = security_test_client.get('/test_user')
    assert b'No logged in user' in res.content


def test_incorrect_secret_key_in_token(session, security_test_client):
    user = LoginUser(**LOGIN_DATA)
    incorrect_token = create_jwt_token(user, JWT_KEY="wrong secret key")
    security_test_client.post('/register', data=REGISTER_DETAIL)
    url = f"/login?existing_jwt={incorrect_token}"
    security_test_client.post(f'{url}', data=LOGIN_DATA)
    res = security_test_client.get('/protected')
    assert b'Your token is incorrect' in res.content


def test_expired_token(session, security_test_client):
    security_test_client.get('/logout')
    user = LoginUser(**LOGIN_DATA)
    incorrect_token = create_jwt_token(user, JWT_MIN_EXP=-1)
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
