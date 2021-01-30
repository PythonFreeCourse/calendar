from typing import List, Optional

from app.config import email_conf
from app.database.models import Event, User
from fastapi import BackgroundTasks, UploadFile
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from pydantic.errors import EmailError
from sqlalchemy.orm.session import Session

mail = FastMail(email_conf)


def send(
        session: Session, event_used: int, user_to_send: int,
        title: str, background_tasks: BackgroundTasks = BackgroundTasks
) -> bool:
    """This function is being used to send emails in the background.
    It takes an event and a user and it sends the event to the user.

    Args:
        session(Session): The session to redirect to the database.
        title (str): Title of the email that is being sent.
        event_used (int): Id number of the event that is used.
        user_to_send (int): Id number of user that we want to notify.
        background_tasks (BackgroundTasks): Function from fastapi that lets
            you apply tasks in the background.

    Returns:
        bool: Returns True if the email was sent, else returns False.
    """
    event_used = session.query(Event).filter(
        Event.id == event_used).first()
    user_to_send = session.query(User).filter(
        User.id == user_to_send).first()
    if not user_to_send or not event_used:
        return False
    if not verify_email_pattern(user_to_send.email):
        return False

    subject = f"{title} {event_used.title}"
    recipients = {"email": [user_to_send.email]}.get("email")
    body = f"begins at:{event_used.start} : {event_used.content}"

    background_tasks.add_task(send_internal, subject=subject, recipients=recipients, body=body)
    return True


async def send_internal(subject: str,
                        recipients: List[str],
                        body: str,
                        subtype: Optional[str] = None,
                        file_attachments: Optional[List[str]] = None):
    if file_attachments is None:
        file_attachments = []

    message = MessageSchema(
         subject=subject,
         recipients=[EmailStr(recipient) for recipient in recipients],
         body=body,
         subtype=subtype,
         attachments=[UploadFile(file_attachment) for file_attachment in file_attachments])

    return await send_internal_internal(message)


async def send_internal_internal(msg: MessageSchema):
    """
    This function receives message and
    configuration as parameters and sends the message.
    :param msg: MessageSchema, message
    :return: None
    """
    await mail.send_message(msg)


def verify_email_pattern(email: str) -> bool:
    """
    This function checks the correctness
    of the entered email address
    :param email: str, the entered email address
    :return: bool,
    True if the entered email address is correct,
    False if the entered email address is incorrect.
    """
    try:
        EmailStr.validate(email)
        return True
    except EmailError:
        return False
