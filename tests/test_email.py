import os

import pytest
from app.internal.email import mail
from fastapi import BackgroundTasks

NO_CONFIG = pytest.mark.skipif(
    (
        os.getenv("MAIL_USERNAME") == "a",
        os.getenv("MAIL_PASSWORD") == "a",
        os.getenv("MAIL_FROM") == "a"
    ), reason="Config is not set!"
)


@NO_CONFIG
def test_email_send(client, user, event):
    mail.config.SUPPRESS_SEND = 1
    with mail.record_messages() as outbox:
        response = client.post(
            "/email_send/", data={
                "event_used": event.id, "user_to_send": user.id,
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 1
        assert response.status_code == 303


@NO_CONFIG
def test_failed_email_send(client, user, event):
    mail.config.SUPPRESS_SEND = 1
    with mail.record_messages() as outbox:
        response = client.post(
            "/email_send/", data={
                "event_used": event.id + 1, "user_to_send": user.id,
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 0
        assert response.status_code == 404
