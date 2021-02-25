import pytest
from starlette.status import HTTP_302_FOUND

from app.internal.email import mail
from app.internal.security.ouath2 import create_jwt_token
from app.internal.security.schema import ForgotPassword

REGISTER_DETAIL = {
    "username": "correct_user",
    "full_name": "full_name",
    "password": "correct_password",
    "confirm_password": "correct_password",
    "email": "example@email.com",
    "description": "",
}

FORGOT_PASSWORD_BAD_DETAILS = [
    ("", ""),
    ("", "example@email.com"),
    ("correct_user", ""),
    ("incorrect_user", "example@email.com"),
    ("correct_user", "inncorrect@email.com"),
]

FORGOT_PASSWORD_DETAILS = {
    "username": "correct_user",
    "email": "example@email.com",
}

RESET_PASSWORD_BAD_CREDENTIALS = [
    ("", "", ""),
    ("correct_user", "", "new_password"),
    ("", "new_password", "new_password"),
    ("correct_user", "new_password", ""),
    ("wrong_user", "new_password", "new_password"),
    ("correct_user", "", "new_password"),
    ("correct_user", "new_password", ""),
    ("correct_user", "new_password", "new_password1"),
]

RESET_PASSWORD_DETAILS = {
    "username": "correct_user",
    "password": "new_password",
    "confirm-password": "new_password",
}


def test_forgot_password_route_ok(security_test_client):
    response = security_test_client.get(
        security_test_client.app.url_path_for("forgot_password_form"),
    )
    assert response.ok


@pytest.mark.parametrize("username, email", FORGOT_PASSWORD_BAD_DETAILS)
def test_forgot_password_bad_details(
    session,
    security_test_client,
    username,
    email,
):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    data = {"username": username, "email": email}
    res = security_test_client.post(
        security_test_client.app.url_path_for("forgot_password"),
        data=data,
    )
    assert b"Please check your credentials" in res.content


def test_email_send(session, security_test_client, smtpd):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    mail.config.SUPPRESS_SEND = 1
    mail.config.MAIL_SERVER = smtpd.hostname
    mail.config.MAIL_PORT = smtpd.port
    mail.config.USE_CREDENTIALS = False
    mail.config.MAIL_TLS = False
    with mail.record_messages() as outbox:
        response = security_test_client.post(
            security_test_client.app.url_path_for("forgot_password"),
            data=FORGOT_PASSWORD_DETAILS,
        )
        assert len(outbox) == 1
        assert b"Email for reseting password was sent" in response.content
        assert "reset password" in outbox[0]["subject"]


def test_reset_password_GET_without_token(session, security_test_client):
    res = security_test_client.get(
        security_test_client.app.url_path_for("reset_password_form"),
    )
    assert b"Verification token is missing" in res.content


def test_reset_password_GET_with_token(session, security_test_client):
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    params = f"?email_verification_token={token}"
    res = security_test_client.get(
        security_test_client.app.url_path_for("reset_password_form")
        + f"{params}",
    )
    assert b"Please choose a new password" in res.content


@pytest.mark.parametrize(
    "username, password, confirm_password",
    RESET_PASSWORD_BAD_CREDENTIALS,
)
def test_reset_password_bad_details(
    session,
    security_test_client,
    username,
    password,
    confirm_password,
):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    data = {
        "username": username,
        "password": password,
        "confirm_password": confirm_password,
    }
    params = f"?email_verification_token={token}"
    res = security_test_client.post(
        security_test_client.app.url_path_for("reset_password") + f"{params}",
        data=data,
    )
    assert b"Please check your credentials" in res.content


def test_reset_password_successfully(session, security_test_client):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    params = f"?email_verification_token={token}"
    res = security_test_client.post(
        security_test_client.app.url_path_for("reset_password") + f"{params}",
        data=RESET_PASSWORD_DETAILS,
    )
    print(res.content)
    assert res.status_code == HTTP_302_FOUND


def test_reset_password_expired_token(session, security_test_client):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=-1)
    params = f"?email_verification_token={token}"
    res = security_test_client.post(
        security_test_client.app.url_path_for("reset_password") + f"{params}",
        data=RESET_PASSWORD_DETAILS,
    )
    assert res.ok


LOGIN_DATA = {"username": "correct_user", "password": "correct_password"}


def test_is_logged_in_with_reset_password_token(session, security_test_client):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    params = f"?existing_jwt={token}"
    security_test_client.post(
        security_test_client.app.url_path_for("login") + f"{params}",
        data=LOGIN_DATA,
    )
    res = security_test_client.get(
        security_test_client.app.url_path_for("is_logged_in"),
    )
    assert b"Your token is not valid" in res.content


def test_is_manager_with_reset_password_token(session, security_test_client):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    params = f"?existing_jwt={token}"
    security_test_client.post(
        security_test_client.app.url_path_for("login") + f"{params}",
        data=LOGIN_DATA,
    )
    res = security_test_client.get(
        security_test_client.app.url_path_for("is_manager"),
    )
    assert b"have a permition to enter this page" in res.content


def test_current_user_with_reset_password_token(session, security_test_client):
    security_test_client.post("/register", data=REGISTER_DETAIL)
    user = ForgotPassword(**FORGOT_PASSWORD_DETAILS)
    token = create_jwt_token(user, jwt_min_exp=15)
    params = f"?existing_jwt={token}"
    security_test_client.post(
        security_test_client.app.url_path_for("login") + f"{params}",
        data=LOGIN_DATA,
    )
    res = security_test_client.get(
        security_test_client.app.url_path_for("current_user"),
    )
    assert b"Your token is not valid" in res.content
