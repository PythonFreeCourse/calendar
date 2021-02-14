from datetime import datetime, date, time
from operator import attrgetter
from typing import List, Dict, Optional, Any

from fastapi import HTTPException
from requests import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.database.models import Task, User
from app.dependencies import logger
from app.internal.utils import create_model


def create_task(db, title, description, date, time, owner_id,
                is_important) -> Task:
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
    return task


def sort_by_time(tasks: List[Task]) -> List[Task]:
    """Sorts the tasks by the start of the task."""

    temp = tasks.copy()
    return sorted(temp, key=attrgetter('time'))


def by_id(db, task_id):
    task = db.query(Task).filter_by(id=task_id).one()
    return task
