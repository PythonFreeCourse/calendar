
from app.internal.email import mail
from fastapi import BackgroundTasks


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


def test_failed_email_send(client, user, event):
    mail.config.MAIL_DEBUG = 1
    mail.config.SUPPRESS_SEND = 1
    mail.config.USE_CREDENTIALS = False
    with mail.record_messages() as outbox:
        response = client.post(
            "/email_send/", data={
                "event_used": event.id + 1, "user_to_send": user.id,
                "title": "Testing",
                "background_tasks": BackgroundTasks})
        assert len(outbox) == 0
        assert response.status_code == 404
