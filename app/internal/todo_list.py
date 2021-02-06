from datetime import datetime
from operator import attrgetter
from typing import List
from urllib.request import Request

from fastapi import Depends
from requests import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db
from app.database.models import Task, UserTask
from app.internal.utils import create_model
from app.main import router
from app.routers.event import by_id


def create_task(db, title, description, date, time, owner_id, is_important=None) -> Task:
    """Creates and saves a new task."""

    task = create_model(
        db, Task,
        title=title,
        description=description,
        date=date,
        time=time,
        owner_id=owner_id,
        is_important=is_important,
        is_done=False
    )
    create_model(
        db, UserTask,
        user_id=owner_id,
        task_id=task.id
    )
    return task


def sort_by_time(tasks: List[Task]) -> List[Task]:
    """Sorts the tasks by the start of the task."""

    temp = tasks.copy()
    return sorted(temp, key=attrgetter('time'))


def get_tasks(session: Session, **param):
    """Returns all tasks filter by param."""

    try:
        tasks = list(session.query(Task).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return tasks


def is_date_before(date: datetime) -> bool:
    """Check if the start date is earlier than the end date"""

    return date < datetime.now()


@router.delete("/{task_id}")
def delete_task(request: Request,
                 task_id: int,
                 db: Session = Depends(get_db)):

    # TODO: Check if the user is the owner of the task.
    task = by_id(db, task_id)
    participants = get_participants_emails_by_task(db, task_id)
    try:
        # Delete task
        db.delete(task)

        # Delete user_task
        db.query(UserTask).filter(UserTask.task_id == task_id).delete()

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "task/taskview.html", {"request": request, "task_id": task_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if participants and task.start > datetime.now():
        pass
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url="/calendar", status_code=status.HTTP_200_OK)