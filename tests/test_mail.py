import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi_mail import MessageSchema
from pydantic import ValidationError, EmailStr

import config
from app.main import app
from internal.mail import send_fast_email

pytest_plugins = "smtpdfix"

client = TestClient(app)


@pytest.fixture
def configured_smtpd(smtpd):
    """
    Overrides the SMTP related configuration to use a mock SMTP server
    :param smtpd: the smtpdfix fixture that represents an SMTP server
    :return: smtpd
    """

    def override_settings():
        return config.Settings(smtp_server=smtpd.hostname,
                               smtp_port=smtpd.port)

    app.dependency_overrides[config.get_settings] = override_settings
    yield smtpd
    app.dependency_overrides.pop(config.get_settings)


def assert_validation_error_missing_body_fields(validation_msg,
                                                missing_fields):
    """
    helper function for asserting with open api validation errors
    look at https://fastapi.tiangolo.com/tutorial/path-params/#data-validation
    :param validation_msg: the response message after json
    :param missing_fields: a list of fields that are asserted missing
    """
    assert isinstance(validation_msg, dict)
    assert 1 == len(validation_msg)
    assert "detail" in validation_msg
    details = validation_msg["detail"]
    assert isinstance(details, list)
    assert len(missing_fields) == len(details)
    for detail in details:
        assert 3 == len(detail)
        assert "type" in detail
        assert "value_error.missing" == detail["type"]
        assert "msg" in detail
        assert "field required" == detail["msg"]
        assert "loc" in detail
        loc = detail["loc"]
        assert isinstance(loc, list)
        assert 2 == len(loc)
        assert "body" == loc[0]
        assert loc[1] in missing_fields


def test_read_main():
    response = client.get("/")
    assert response.ok


def test_send_mail_no_body(configured_smtpd):
    response = client.post("/mail/invitation/")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{
        'loc': ['body'],
        'msg': 'field required',
        'type': 'value_error.missing'}]}
    assert not configured_smtpd.messages


@pytest.mark.parametrize("body, missing_fields", [
    (
            {"sender_name": "string", "recipient_name": "string"},
            ["recipient_mail"],
    ),

    (
            {"sender_name": "string", "recipient_mail": "test@mail.com"},
            ["recipient_name"],
    ),
    (
            {"recipient_name": "string", "recipient_mail": "test@mail.com"},
            ["sender_name"],
    ),
    (
            {"sender_name": "string"},
            ["recipient_name", "recipient_mail"],
    ),
    (
            {"recipient_name": "string"},
            ["sender_name", "recipient_mail"],
    ),
    (
            {"recipient_mail": "test@mail.com"},
            ["sender_name", "recipient_name"],
    ),
])
def test_send_mail_partial_body(body, missing_fields,
                                configured_smtpd):
    response = client.post("/mail/invitation/", json=body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_validation_error_missing_body_fields(response.json(),
                                                missing_fields)
    assert not configured_smtpd.messages


def test_send_mail_invalid_email(configured_smtpd):
    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test#mail.com"
    })

    assert response.ok
    assert response.json() == {'message': "Please enter valid email address"}
    assert not configured_smtpd.messages


def test_send_mail_valid_email(configured_smtpd):
    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test@mail.com"
    }
                           )
    assert response.ok
    assert response.json() == {
        'message': 'Your message was sent successfully to string'}
    assert len(configured_smtpd.messages) == 1


# internal mail checks
@pytest.mark.asyncio
async def test_internal_send_fast_email(smtpd):
    message = MessageSchema(
        subject="Invitation",
        recipients=[EmailStr("recipient@mail.com")],
        body="<html><head></head><body></body></html>",
        subtype="html",
    )

    await send_fast_email(message, config.Settings(
        smtp_server=smtpd.hostname, smtp_port=smtpd.port))
    assert len(smtpd.messages) == 1


@pytest.mark.asyncio
async def test_internal_send_fast_email_invalid_email(smtpd):
    with pytest.raises(ValidationError):
        message = MessageSchema(
            subject="Invitation",
            recipients=[EmailStr("recipient#mail.com")],
            body="<html><head></head><body></body></html>",
            subtype="html",
        )

        await send_fast_email(message, config.Settings(
            smtp_server=smtpd.hostname, smtp_port=smtpd.port))
    assert not smtpd.messages
