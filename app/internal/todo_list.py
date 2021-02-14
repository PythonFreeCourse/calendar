from operator import attrgetter
from typing import List

from app.database.models import Task
from app.internal.utils import create_model


def create_task(db, title, description, datestr, timestr, owner_id,
                is_important) -> Task:
    """Creates and saves a new task."""

    task = create_model(
        db, Task,
        title=title,
        description=description,
        date=datestr,
        time=timestr,
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
