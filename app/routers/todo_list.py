from datetime import datetime

from fastapi import Depends, APIRouter, Form
from requests import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.responses import RedirectResponse

from app.config import templates
from app.database.database import get_db
from app.database.models import User
from app.internal.todo_list import create_task, by_id

router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)


@router.post("/delete")
def delete_task(taskId: int = Form(...), db: Session = Depends(get_db)):
    # TODO: Check if the user is the owner of the task.
    task = by_id(db, taskId)
    datestr = task.date.strftime('%Y-%m-%d')
    try:
        # Delete task
        db.delete(task)

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "dayview.html", {"task_id": taskId},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url=f"/day/{datestr}", status_code=302)


@router.post("/add")
async def add_task(title: str = Form(...), description: str = Form(...),
                   datestr: str = Form(...), timestr: str = Form(...),
                   is_important: bool = Form(False), session=Depends(get_db)):
    # TODO: add a login session
    user = session.query(User).filter_by(username='test1').first()
    create_task(session, title, description,
                datetime.strptime(datestr, '%Y-%m-%d')
                .date(), datetime.strptime(timestr, '%H:%M:%S').time(),
                user.id, is_important)
    return RedirectResponse(f"/day/{datestr}", status_code=303)


@router.post("/edit")
async def edit_task(task_id: int = Form(...), title: str = Form(...),
                    description: str = Form(...),
                    datestr: str = Form(...), timestr: str = Form(...),
                    is_important: bool = Form(False), session=Depends(get_db)):
    task = by_id(session, task_id)
    task.title = title
    task.description = description
    task.date = datetime.strptime(datestr, '%Y-%m-%d').date()
    task.time = datetime.strptime(timestr, '%H:%M:%S').time()
    task.is_important = is_important
    session.commit()
    return RedirectResponse(f"/day/{datestr}", status_code=303)


@router.post("/setDone/{task_id}")
async def set_task_done(task_id: int, session=Depends(get_db)):
    task = by_id(session, task_id)
    task.is_done = True
    session.commit()
    return RedirectResponse(f"/day/{task.date.strftime('%Y-%m-%d')}", status_code=303)


@router.post("/setUndone/{task_id}")
async def set_task_undone(task_id: int, session=Depends(get_db)):
    task = by_id(session, task_id)
    task.is_done = False
    session.commit()
    return RedirectResponse(f"/day/{task.date.strftime('%Y-%m-%d')}", status_code=303)