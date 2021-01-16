import os

import pytest
from app.internal.email import fm
from fastapi import BackgroundTasks

NO_CONFIG = pytest.mark.skipif(
    os.getenv("MAIL_USERNAME") is None, reason="Config is not set!"
)


@NO_CONFIG
def test_email_send(client, sessions):
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(
            "/emailbackground", data={
                "event_used": "1", "user_to_send": "1",
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 1
        assert response.status_code == 303


@NO_CONFIG
def test_failed_email_send(client, sessions):
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(
            "/emailbackground", data={
                "event_used": "10", "user_to_send": "1",
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 0
        assert response.status_code == 303
