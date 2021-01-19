from app.database.database import get_db
from app.internal.email import send
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/email_send",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def send_email(
    db: Session = Depends(get_db),
    send_to: str = "/",
    title: str = Form(...),
    event_used: str = Form(...),
    user_to_send: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks
) -> RedirectResponse:
    if not send(
            title=title, event_used=event_used,
            user_to_send=user_to_send,
            background_tasks=background_tasks, session=db):
        raise HTTPException(status_code=404, detail="Couldn't send the email!")
    return RedirectResponse(send_to, status_code=303)
