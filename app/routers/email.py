from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException
from pydantic import BaseModel, EmailStr
from pydantic.errors import EmailError
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse

from app.dependencies import get_db
from app.internal.email import send as internal_send
from app.internal.email import send_email_invitation

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)


@router.post("/send")
async def send(
        db: Session = Depends(get_db),
        send_to: str = "/",
        title: str = Form(...),
        event_used: str = Form(...),
        user_to_send: str = Form(...),
        background_tasks: BackgroundTasks = BackgroundTasks
) -> RedirectResponse:
    if not internal_send(
            title=title, event_used=event_used,
            user_to_send=user_to_send,
            background_tasks=background_tasks, session=db):
        raise HTTPException(status_code=404, detail="Couldn't send the email!")
    return RedirectResponse(send_to, status_code=303)


INVALID_EMAIL_ADDRESS_ERROR_MESSAGE = "Please enter valid email address"
SUCCESSFULLY_SENT_EMAIL_MESSAGE = "Your message was sent successfully"


class InvitationParams(BaseModel):
    send_to: str = "/"
    sender_name: str
    recipient_name: str
    recipient_mail: str


@router.post("/invitation/")
def send_invitation(invitation: InvitationParams,
                    background_task: BackgroundTasks):
    """
    This function sends the recipient an invitation
    to his email address in the format HTML.
    :param invitation: InvitationParams, invitation parameters
    :param background_task: BackgroundTasks
    :return: json response message,
    error message if the entered email address is incorrect,
    confirmation message if the invitation was successfully sent
    """
    try:
        EmailStr.validate(invitation.recipient_mail)
    except EmailError:
        raise HTTPException(
            status_code=422,
            detail=INVALID_EMAIL_ADDRESS_ERROR_MESSAGE)

    if not send_email_invitation(
            sender_name=invitation.sender_name,
            recipient_name=invitation.recipient_name,
            recipient_mail=invitation.recipient_mail,
            background_tasks=background_task):
        raise HTTPException(status_code=422, detail="Couldn't send the email!")
    return RedirectResponse(invitation.send_to, status_code=303)
