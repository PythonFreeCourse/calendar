from fastapi import APIRouter, Depends, Request
from app.internal.timer import get_next_user_event_start_time
from app.database.models import User
from app.dependencies import get_db


router = APIRouter()


@router.get("/timer")
def timer(request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    return get_next_user_event_start_time(session, user.id)
