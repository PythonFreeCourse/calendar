from app.internal.email_use import fm
from fastapi import BackgroundTasks
import pytest


@pytest.mark.skip(reason="Config need to be set")
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


@pytest.mark.skip(reason="Config need to be set")
def test_failed_email_send(client, sessions):
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(
            "/emailbackground", data={
                "event_used": "2", "user_to_send": "1",
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 0
        assert response.status_code == 303
