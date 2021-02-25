from datetime import date, time

from sqlalchemy.orm import Session

from app.database.models import Task
from app.internal.utils import create_model


def create_task(
        db: Session,
        title: str,
        description: str,
        date_str: date,
        time_str: time,
        owner_id: int,
        is_important: bool,
) -> Task:
    """Creates and saves a new task."""
    task = create_model(
        db,
        Task,
        title=title,
        description=description,
        date=date_str,
        time=time_str,
        owner_id=owner_id,
        is_important=is_important,
        is_done=False,
    )
    return task


def by_id(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter_by(id=task_id).one()
    return task
