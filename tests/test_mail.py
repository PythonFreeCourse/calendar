import pytest
from fastapi.testclient import TestClient
from fastapi_mail import MessageSchema
from pydantic import ValidationError

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


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_send_mail_no_body(configured_smtpd):
    response = client.post("/mail/invitation/")
    assert response.status_code == 422
    assert response.json() == {'detail': [{
        'loc': ['body'],
        'msg': 'field required',
        'type': 'value_error.missing'}]}
    assert len(configured_smtpd.messages) == 0


@pytest.mark.parametrize("body,expected_json", [
    (
            {"sender_name": "string", "recipient_name": "string"},
            {'detail': [{
                'loc': ['body', 'recipient_mail'],
                'msg': 'field required',
                'type': 'value_error.missing'}]},
    ),

    (
            {"sender_name": "string", "recipient_mail": "test@mail.com"},
            {'detail': [{
                'loc': ['body', 'recipient_name'],
                'msg': 'field required',
                'type': 'value_error.missing'}]},
    ),
    (
            {"recipient_name": "string", "recipient_mail": "test@mail.com"},
            {'detail': [{
                'loc': ['body', 'sender_name'],
                'msg': 'field required',
                'type': 'value_error.missing'}]},
    ),
    (
            {"sender_name": "string"},
            {'detail': [
                {'loc': ['body', 'recipient_name'],
                 'msg': 'field required',
                 'type': 'value_error.missing'},
                {'loc': ['body', 'recipient_mail'],
                 'msg': 'field required',
                 'type': 'value_error.missing'}
            ]}
    ),
    (
            {"recipient_name": "string"},
            {'detail': [
                {'loc': ['body', 'sender_name'],
                 'msg': 'field required',
                 'type': 'value_error.missing'},
                {'loc': ['body', 'recipient_mail'],
                 'msg': 'field required',
                 'type': 'value_error.missing'}
            ]}
    ),
    (
            {"recipient_mail": "test@mail.com"},
            {'detail': [
                {'loc': ['body', 'sender_name'],
                 'msg': 'field required',
                 'type': 'value_error.missing'},
                {'loc': ['body', 'recipient_name'],
                 'msg': 'field required',
                 'type': 'value_error.missing'}
            ]}
    ),
])
def test_send_mail_partial_body(body, expected_json,
                                configured_smtpd):
    response = client.post("/mail/invitation/", json=body)
    assert response.status_code == 422
    assert response.json() == expected_json
    assert len(configured_smtpd.messages) == 0


def test_send_mail_invalid_email(configured_smtpd):
    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test#mail.com"
    })

    assert response.status_code == 200
    assert response.json() == {'message': "Please enter valid email address"}
    assert len(configured_smtpd.messages) == 0


def test_send_mail_valid_email(configured_smtpd):
    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test@mail.com"
    }
                           )
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Your message was sent successfully to string'}
    assert len(configured_smtpd.messages) == 1


# internal mail checks
@pytest.mark.asyncio
async def test_internal_send_fast_email(smtpd):
    message = MessageSchema(
        subject="Invitation",
        recipients=["recipient@mail.com"],
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
            recipients=["recipient#mail.com"],
            body="<html><head></head><body></body></html>",
            subtype="html",
        )

        await send_fast_email(message, config.Settings(
            smtp_server=smtpd.hostname, smtp_port=smtpd.port))
    assert len(smtpd.messages) == 0
