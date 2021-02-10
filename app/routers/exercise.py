from fastapi import APIRouter, Depends, Request
from app.database.models import User
from app.dependencies import get_db, templates
from app.routers.user_exercise import get_user_exercise
from datetime import datetime
from app import config
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/exercise",
    tags=["exercise"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def exercise(
        request: Request,
        session: Session = Depends(get_db),
        ):
    """
    If is active exercise = True
    Show user exercise for a specific day if is_active_exercise is ture.
    """
    user = session.query(User).filter_by(id=1).first()
    if not user:
        # create empty default user
        user = User(
            username='',
            password='',
            email=''
        )
    # Get user exercise
    user_exercise = get_user_exercise(session, user_id=user.id)
    if user_exercise:
        # Get exercise day
        delta = datetime.now() - user_exercise[0].start_date
        # All exercises split to 30 days
        day = (delta.days % 30) + 1
    else:
        day = 1
    exercise_day = str(config.EXERCISE_FILE.format(num=day))
    return templates.TemplateResponse("exercise.html", {
        "request": request,
        "user": user,
        "exercise": exercise_day
    })
