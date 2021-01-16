import os
from app.database.models import Event, User
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from sqlalchemy.orm.session import Session

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)
fm = FastMail(conf)


def send_basic_email(
        sessions: Session, event_used: str, user_to_send: str,
        title: str,
        background_tasks: BackgroundTasks = BackgroundTasks) -> bool:
    """This function is being used to send emails in the background.
    It takes an event and a user and it sends the event to the user.

    Args:
        sessions(Session): The session to redirect to the database.
        title (str): Title of the email that is being sent.
        event_used (str): Id number of the event that is used.
        user_to_send (str): Id number of user that we want to notify.
        background_tasks (BackgroundTasks): Function from fastapi that lets
            you apply tasks in the background.

    Returns:
        bool: Returns True if the email was sent, else returns False.
    """
    event_used = sessions.query(Event).filter(
        Event.id == event_used).first()
    user_to_send = sessions.query(User).filter(
        User.id == user_to_send).first()
    if not user_to_send or not event_used:
        return False
    message = MessageSchema(
        subject=f"{title} {event_used.title}",
        recipients={"email": [user_to_send.email]}.get("email"),
        body=f"{event_used.date} : {event_used.content}",
    )
    background_tasks.add_task(fm.send_message, message)
    return True
