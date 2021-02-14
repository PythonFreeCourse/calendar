import pytest
from app.internal.security.ouath2 import create_jwt_token, LoginUser
from app.internal.security.reset_password import mail, send_mail
from starlette.status import HTTP_302_FOUND
from app.internal.security.ouath2 import create_jwt_token, ForgotPassword
from app.config import CALENDAR_RESET_PASSWORD_PAGE


REGISTER_DETAIL = {
    'username': 'correct_user', 'full_name': 'full_name',
    'password': 'correct_password', 'confirm_password': 'correct_password',
    'email': 'example@email.com', 'description': ""}


FORGOT_PASSWORD_DETAILS = {'username': 'correct_user', 'email': 'example@email.com'}


def test_login_route_ok(security_test_client):
    response = security_test_client.get("/forgot-password")
    assert response.ok


def test_email_send(session, security_test_client, smtpd):
    security_test_client.post('/register', data=REGISTER_DETAIL)
    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    mail.config.USE_CREDENTIALS = False
    mail.config.MAIL_TLS = False
    with mail.record_messages() as outbox:
        response = security_test_client.post("/forgot-password", data=FORGOT_PASSWORD_DETAILS)
        assert len(outbox) == 1
        assert b'Email for reseting password was sent' in response.content
        assert 'reset password' in outbox[0]['subject']


def test_reset_password_GET_without_token(session, security_test_client):
    user = ForgotPassword(user_id=1, **FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, JWT_MIN_EXP=15)
    link = f"{CALENDAR_RESET_PASSWORD_PAGE}"
    res = security_test_client.get(link)
    assert b'Verification token is missing' in res.content


def test_reset_password_GET_with_token(session, security_test_client):
    user = ForgotPassword(user_id=1, **FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, JWT_MIN_EXP=15)
    link = f"{CALENDAR_RESET_PASSWORD_PAGE}?token={token}"
    res = security_test_client.get(link)
    assert b'Please choose a new password' in res.content


# def test_reset_password_POST_with_legal_token(session, security_test_client):
#     user = ForgotPassword(user_id=1, **FORGOT_PASSWORD_DETAILS)
#     expired_token = create_jwt_token(user, JWT_MIN_EXP=15)
#     link = f"{CALENDAR_RESET_PASSWORD_PAGE}?token={user.token}"
#     res = security_test_client.get(link)
#     assert b'Please choose a new password' in res.content



    
    
    