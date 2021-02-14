import os
from typing import List, Optional

from fastapi import BackgroundTasks, UploadFile
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from pydantic.errors import EmailError
from sqlalchemy.orm.session import Session

from app.config import (CALENDAR_HOME_PAGE, CALENDAR_REGISTRATION_PAGE,
                        CALENDAR_SITE_NAME, email_conf, templates)
from app.database.models import Event, User

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

    background_tasks.add_task(send_internal,
                              subject=subject,
                              recipients=recipients,
                              body=body)
    return True


def send_email_invitation(sender_name: str,
                          recipient_name: str,
                          recipient_mail: str,
                          background_tasks: BackgroundTasks = BackgroundTasks
                          ) -> bool:
    """
    This function takes as parameters the sender's name,
    the recipient's name and his email address, configuration, and
    sends the recipient an invitation to his email address in
    the format HTML.
    :param sender_name: str, the sender's name
    :param recipient_name: str, the recipient's name
    :param recipient_mail: str, the recipient's email address
    :param background_tasks: (BackgroundTasks): Function from fastapi that lets
            you apply tasks in the background.
    :return: bool, True if the invitation was successfully
    sent to the recipient, and False if the entered
    email address is incorrect.
    """
    if not verify_email_pattern(recipient_mail):
        return False

    if not recipient_name:
        return False

    if not sender_name:
        return False

    template = templates.get_template("invite_mail.html")
    html = template.render(recipient=recipient_name, sender=sender_name,
                           site_name=CALENDAR_SITE_NAME,
                           registration_link=CALENDAR_REGISTRATION_PAGE,
                           home_link=CALENDAR_HOME_PAGE,
                           addr_to=recipient_mail)

    subject = "Invitation"
    recipients = [recipient_mail]
    body = html
    subtype = "html"

    background_tasks.add_task(send_internal,
                              subject=subject,
                              recipients=recipients,
                              body=body,
                              subtype=subtype)
    return True


def send_email_file(file_path: str,
                    recipient_mail: str,
                    background_tasks: BackgroundTasks = BackgroundTasks):
    """
    his function takes as parameters the file's path,
    the recipient's email address, configuration, and
    sends the recipient an file to his email address.
    :param file_path: str, the file's path
    :param recipient_mail: str, the recipient's email address
    :param background_tasks: (BackgroundTasks): Function from fastapi that lets
            you apply tasks in the background.
    :return: bool, True if the file was successfully
    sent to the recipient, and False if the entered
    email address is incorrect or file does not exist.
    """
    if not verify_email_pattern(recipient_mail):
        return False

    if not os.path.exists(file_path):
        return False

    subject = "File"
    recipients = [recipient_mail]
    body = "file"
    file_attachments = [file_path]

    background_tasks.add_task(send_internal,
                              subject=subject,
                              recipients=recipients,
                              body=body,
                              file_attachments=file_attachments)
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
        attachments=[UploadFile(file_attachment)
                     for file_attachment in file_attachments])

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
