import os

from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr
from pydantic.errors import EmailError

from app import config

templates = Jinja2Templates(directory=os.path.join("app", "templates"))

# application name
CALENDAR_SITE_NAME = "Calendar"
# link to the home page of the application
CALENDAR_HOME_PAGE = "calendar.pythonic.guru"
# link to the application registration page
CALENDAR_REGISTRATION_PAGE = r"calendar.pythonic.guru/registration"


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


async def send_fast_email(msg: MessageSchema,
                          settings: config.Settings):
    """
    This function receives message and
    configuration as parameters and sends the message.
    :param msg: MessageSchema, message
    :param settings: Settings, configuration
    :return: None
    """
    mail_conf = ConnectionConfig(
        MAIL_USERNAME=settings.smtp_username,
        MAIL_PASSWORD=settings.smtp_password,
        MAIL_FROM=EmailStr(settings.smtp_from_email),
        MAIL_PORT=settings.smtp_port,
        MAIL_SERVER=settings.smtp_server,
        MAIL_TLS=settings.smtp_use_tls,
        MAIL_SSL=settings.smtp_use_ssl,
        USE_CREDENTIALS=settings.smtp_use_credentials,
    )
    fast_mail = FastMail(mail_conf)
    await fast_mail.send_message(msg)


async def send_fast_email_invitation(sender_name: str, recipient_name: str,
                                     recipient_mail: str,
                                     settings: config.Settings):
    """
    This function takes as parameters the sender's name,
    the recipient's name and his email address, configuration, and
    sends the recipient an invitation to his email address in
    the format HTML.
    :param sender_name: str, the sender's name
    :param recipient_name: str, the recipient's name
    :param recipient_mail: str, the recipient's email address
    :param settings: Settings, configuration
    :return: bool, True if the invitation was successfully
    sent to the recipient, and False if the entered
    email address is incorrect.
    """
    if not verify_email_pattern(recipient_mail):
        return False

    template = templates.get_template("invite_mail.html")
    html = template.render(recipient=recipient_name, sender=sender_name,
                           site_name=CALENDAR_SITE_NAME,
                           registration_link=CALENDAR_REGISTRATION_PAGE,
                           home_link=CALENDAR_HOME_PAGE,
                           addr_to=recipient_mail)

    message = MessageSchema(
        subject="Invitation",
        recipients=[EmailStr(recipient_mail)],
        body=html,
        subtype="html",
    )

    await send_fast_email(message, settings)
    return True
