from fastapi import BackgroundTasks, APIRouter
from pydantic import BaseModel, EmailStr
from pydantic.errors import EmailError

from internal.mail import send_fast_email_invitation

router = APIRouter()

CORRECT_EMAIL_ADDRESS_ERROR_MESSAGE = "Please enter valid email address"
SUCCESSFULLY_SENT_EMAIL_MESSAGE = "Your message was sent successfully"


class InvitationParams(BaseModel):
    sender_name: str
    recipient_name: str
    recipient_mail: str


@router.post("/mail/invitation/")  # response_class=HTMLResponse ?
def send_invitation(invitation: InvitationParams, background_task: BackgroundTasks):
    try:
        EmailStr.validate(invitation.recipient_mail)
    except EmailError:
        return {"message": f"{CORRECT_EMAIL_ADDRESS_ERROR_MESSAGE}"}

    background_task.add_task(send_fast_email_invitation,
                             sender_name=invitation.sender_name,
                             recipient_name=invitation.recipient_name,
                             recipient_mail=invitation.recipient_mail
                             )

    return {"message": f"{SUCCESSFULLY_SENT_EMAIL_MESSAGE} to {invitation.recipient_name}"}
