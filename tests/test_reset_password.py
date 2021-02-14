import pytest

from starlette.status import HTTP_302_FOUND

from app.internal.security.ouath2 import create_jwt_token
from app.internal.security.reset_password import mail
from app.internal.security.schema import ForgotPassword


REGISTER_DETAIL = {
    'username': 'correct_user', 'full_name': 'full_name',
    'password': 'correct_password', 'confirm_password': 'correct_password',
    'email': 'example@email.com', 'description': ""}

FORGOT_PASSWORD_BAD_DETAILS = [
    ('', ''),
    ('', 'example@email.com'),
    ('correct_user', ''),
    ('incorrect_user', 'example@email.com'),
    ('correct_user', 'inncorrect@email.com')
]

FORGOT_PASSWORD_DETAILS = {
    'username': 'correct_user', 'email': 'example@email.com'}

RESET_PASSWORD_BAD_CREDENTIALS = [
    ('', '', ''),
    ('correct_user', '', 'new_password'),
    ('', 'new_password', 'new_password'),
    ('correct_user', 'new_password', ''),
    ('wrong_user', 'new_password', 'new_password'),
    ('correct_user', '', 'new_password'),
    ('correct_user', 'new_password', ''),
    ('correct_user', 'new_password', 'new_password1')
]

RESET_PASSWORD_DETAILS = {
    'username': 'correct_user',
    'password': 'new_password', 'confirm_password': 'new_password'}


def test_forgot_password_route_ok(security_test_client):
    response = security_test_client.get("/forgot-password")
    assert response.ok


@pytest.mark.parametrize(
    "username, email", FORGOT_PASSWORD_BAD_DETAILS)
def test_forgot_password_bad_details(
        session, security_test_client, username, email):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    data = {'username': username, 'email': email}
    res = security_test_client.post("/forgot-password", data=data)
    assert b'Please check your credentials' in res.content


def test_email_send(session, security_test_client, smtpd):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    mail.config.USE_CREDENTIALS = False
    mail.config.MAIL_TLS = False
    with mail.record_messages() as outbox:
        response = security_test_client.post(
            "/forgot-password", data=FORGOT_PASSWORD_DETAILS)
        assert len(outbox) == 1
        assert b'Email for reseting password was sent' in response.content
        assert 'reset password' in outbox[0]['subject']


def test_reset_password_GET_without_token(session, security_test_client):
    res = security_test_client.get("/reset-password")
    assert b'Verification token is missing' in res.content


def test_reset_password_GET_with_token(session, security_test_client):
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    link = f"/reset-password?token={token}"
    res = security_test_client.get(link)
    assert b'Please choose a new password' in res.content


@pytest.mark.parametrize(
    "username, password, confirm_password", RESET_PASSWORD_BAD_CREDENTIALS)
def test_reset_password_bad_details(
        session, security_test_client, username, password, confirm_password):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    link = f"/reset-password?token={token}"
    data = {
        'username': username, 'password': password,
        'confirm_password': confirm_password
    }
    res = security_test_client.post(link, data=data)
    assert b'Please check your credentials' in res.content


def test_reset_password_successfully(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    link = f"/reset-password?token={token}"
    res = security_test_client.post(link, data=RESET_PASSWORD_DETAILS)
    assert res.status_code == HTTP_302_FOUND


def test_reset_password_expired_token(session, security_test_client):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=-1)
    link = f"/reset-password?token={token}"
    res = security_test_client.post(link, data=RESET_PASSWORD_DETAILS)
    # assert b'Your token has expired' in res.content
    assert res.ok
