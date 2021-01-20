from fastapi import BackgroundTasks, APIRouter, Depends
from pydantic import BaseModel, EmailStr
from pydantic.errors import EmailError

from app import config
from app.internal.mail import send_fast_email_invitation

router = APIRouter()

INVALID_EMAIL_ADDRESS_ERROR_MESSAGE = "Please enter valid email address"
SUCCESSFULLY_SENT_EMAIL_MESSAGE = "Your message was sent successfully"


class InvitationParams(BaseModel):
    sender_name: str
    recipient_name: str
    recipient_mail: str


@router.post("/mail/invitation/")
def send_invitation(invitation: InvitationParams,
                    background_task: BackgroundTasks,
                    settings: config.Settings =
                    Depends(config.get_settings)):
    """
    This function sends the recipient an invitation
    to his email address in the format HTML.
    :param invitation: InvitationParams, invitation parameters
    :param background_task: BackgroundTasks
    :param settings: Settings, configuration
    :return: json response message,
    error message if the entered email address is incorrect,
    confirmation message if the invitation was successfully sent
    """
    try:
        EmailStr.validate(invitation.recipient_mail)
    except EmailError:
        return {"message": f"{INVALID_EMAIL_ADDRESS_ERROR_MESSAGE}"}

    background_task.add_task(send_fast_email_invitation,
                             sender_name=invitation.sender_name,
                             recipient_name=invitation.recipient_name,
                             recipient_mail=invitation.recipient_mail,
                             settings=settings,
                             )

    return {"message": f"{SUCCESSFULLY_SENT_EMAIL_MESSAGE}"
                       f" to {invitation.recipient_name}"}
