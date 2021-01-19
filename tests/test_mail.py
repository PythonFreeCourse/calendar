import pytest
from fastapi.testclient import TestClient
from fastapi_mail import MessageSchema
from pydantic import ValidationError

from app.main import app
from internal.mail import send_fast_email

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_send_mail_no_body():
    response = client.post("/mail/invitation/")
    assert response.status_code == 422
    assert response.json() == {'detail': [{
        'loc': ['body'],
        'msg': 'field required',
        'type': 'value_error.missing'}]}


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
def test_send_mail_partial_body(body, expected_json):
    response = client.post("/mail/invitation/", json=body)
    assert response.status_code == 422
    assert response.json() == expected_json


def test_send_mail_invalid_email():

    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test#mail.com"
    })

    assert response.status_code == 200
    assert response.json() == {'message': "Please enter valid email address"}


def test_send_mail_valid_email():
    response = client.post("/mail/invitation/", json={
        "sender_name": "string",
        "recipient_name": "string",
        "recipient_mail": "test@mail.com"
    }
                           )
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Your message was sent successfully to string'}


# internal mail checks #
@pytest.mark.asyncio
async def test_internal_send_fast_email():
    message = MessageSchema(
        subject="Invitation",
        recipients=["recipient@mail.com"],
        body="<html><head></head><body></body></html>",
        subtype="html",
    )

    await send_fast_email(message)


@pytest.mark.asyncio
async def test_internal_send_fast_email_invalid_email():
    with pytest.raises(ValidationError):
        message = MessageSchema(
            subject="Invitation",
            recipients=["recipient#mail.com"],
            body="<html><head></head><body></body></html>",
            subtype="html",
        )

        await send_fast_email(message)
