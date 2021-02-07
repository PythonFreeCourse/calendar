from datetime import datetime
from urllib.request import Request

from fastapi import Depends, APIRouter
from requests import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.responses import RedirectResponse

from app.config import templates
from app.database.database import get_db
from app.database.models import User
from app.internal.todo_list import create_task

router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)


@router.delete("/{task_id}")
def delete_task(request: Request,
                task_id: int,
                db: Session = Depends(get_db)):
    # TODO: Check if the user is the owner of the task.
    task = by_id(db, task_id)
    try:
        # Delete task
        db.delete(task)

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "dayview.html", {"request": request, "task_id": task_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url="/calendar", status_code=status.HTTP_200_OK)


@router.post("/add")
async def add_task(title: str, description: str, datestr: str, timestr: str,
                   session=Depends(get_db), is_important: bool = False):
    # TODO: add a login session
    user = session.query(User).filter_by(username='test1').first()
    create_task(session, title, description,
                datetime.strptime(datestr, '%Y-%m-%d')
                .date(), datetime.strptime(timestr, '%H:%M').time(),
                user.id, is_important)
    return RedirectResponse(f"/day/{datestr}")
