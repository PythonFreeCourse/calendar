from datetime import datetime
from operator import attrgetter
from typing import List, Dict, Optional, Any

from fastapi import HTTPException
from requests import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.database.models import Task
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


def by_id(db, task_id):
    task = db.query(Task).filter_by(id=task_id).one()
    return task


def is_fields_types_valid(to_check: Dict[str, Any], types: Dict[str, Any]):
    """validate dictionary values by dictionary of types"""
    errors = []
    for field_name, field_type in to_check.items():
        if types[field_name] and not isinstance(field_type, types[field_name]):
            errors.append(
                f"{field_name} is '{type(field_type).__name__}' and"
                + f"it should be from type '{types[field_name].__name__}'")
            logger.warning(errors)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=errors)


def get_task_with_editable_fields_only(task: Dict[str, Any]
                                        ) -> Dict[str, Any]:
    """Remove all keys that are not allowed to update"""

    return {i: task[i] for i in UPDATE_TASKS_FIELDS if i in task}


def _update_task(db: Session, task_id: int, task_to_update: Dict) -> task:
    try:
        # Update database
        db.query(Task).filter(Task.id == task_id).update(
            task_to_update, synchronize_session=False)

        db.commit()
        return by_id(db, task_id)
    except (AttributeError, SQLAlchemyError) as e:
        logger.exception(str(e))
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error")


def update_task(task_id: int, task: Dict, db: Session
                 ) -> Optional[Task]:
    # TODO Check if the user is the owner of the task.
    old_task = by_id(db, task_id)
    task_to_update = get_task_with_editable_fields_only(task)
    is_fields_types_valid(task_to_update, UPDATE_TASKS_FIELDS)
    check_change_dates_allowed(old_task, task_to_update)
    if not task_to_update:
        return None
    task_updated = _update_task(db, task_id, task_to_update)
    # TODO: Send emails to recipients.
    return task_updated