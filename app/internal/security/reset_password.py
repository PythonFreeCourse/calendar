from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session

from app.config import (
    CALENDAR_RESET_PASSWORD_PAGE, CALENDAR_SITE_NAME, email_conf)
from app.dependencies import templates
from app.internal.security.schema import ForgotPassword


mail = FastMail(email_conf)


async def send_mail(
        session: Session, user: ForgotPassword,
        background_tasks: BackgroundTasks) -> bool:
    template = templates.get_template("reset_password_mail.html")
    html = template.render(
         recipient=user.username,
         site_name=CALENDAR_SITE_NAME,
         link=f"{CALENDAR_RESET_PASSWORD_PAGE}?token={user.token}",
         email=user.email)
    message = MessageSchema(
        subject=f"{CALENDAR_SITE_NAME} reset password",
        recipients=[user.email], body=html, subtype='html')
    background_tasks.add_task(mail.send_message, message)
    return True
