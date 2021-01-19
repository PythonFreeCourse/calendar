from app.config import email_conf
from app.database.models import Event, User
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
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
    message = MessageSchema(
        subject=f"{title} {event_used.title}",
        recipients={"email": [user_to_send.email]}.get("email"),
        body=f"begins at:{event_used.start} : {event_used.content}",
    )
    background_tasks.add_task(mail.send_message, message)
    return True
