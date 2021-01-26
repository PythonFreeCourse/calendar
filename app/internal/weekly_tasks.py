from datetime import date ,datetime, time
from typing import Tuple

from app.database.models import User, Task, WeeklyTask
from sqlalchemy.orm.session import Session


def check_inputs(days: str, the_time: time, title: str) -> bool:
    """Checks inputs, used by the make_or_change_weekly_task function"""
    if not days or days == "" or not the_time or not title or title == "":
        return False
    return True


def make_or_change_weekly_task(
    user: User, session: Session,
    mode: str, weekly_task_id: int,
    title: str, days: str,
    content: str, is_important: bool,
    the_time: time) -> Tuple[bool, WeeklyTask]:
    """This function is being used to add a Weekly Task to the user
    or to edit an existing Weekly Task the user have.

    Args:
        user (User): The user who wants to add or edit the Weekly Task.
        session (Session): The session to redirect to the database.
        mode (str): Determines whether in Add or Edit mode.
        weekly_task_id (int): In edit mode, represents the weekly task being edited.
        title (str): Title of the Weekly Task.
        days (str): Return days of the Weekly Task.
        content (str): Content of the Weekly Task.
        is_important (bool): If the task is important.
        the_time (time): Return time of the Weekly Task.

    Returns:
        Tuple: Boolean variable which shows if the change has been made to the db.
            and the model WeeklyTask which the function made so far.
    """
    weekly_task = WeeklyTask(
        title=title,
        content=content,
        is_important=is_important,
        owner_id=user.id
    )

    if weekly_task_id:
        weekly_task.id = weekly_task_id

    inputs_ok = check_inputs(days, the_time, title)
    if not inputs_ok:
        return False, weekly_task

    weekly_task.days = days
    weekly_task.the_time = the_time.strftime("%H:%M")

    if mode == "add":
        user_titles = (user_weekly_task.title for user_weekly_task in user.weekly_tasks)
        if title in user_titles:
            return False, weekly_task
        session.add(weekly_task)
        session.commit()
        return True, weekly_task

    else:  # if mode == "edit"
        old_weekly_task = session.query(WeeklyTask).filter_by(id=weekly_task.id).first()

        user_titles = (
            user_weekly_task.title for user_weekly_task in user.weekly_tasks 
            if user_weekly_task.title != old_weekly_task.title
        )

        if title in user_titles:
            return False, weekly_task

        if old_weekly_task.owner_id != weekly_task.owner_id:
            return False, weekly_task

        old_weekly_task.title = weekly_task.title
        old_weekly_task.days = weekly_task.days
        old_weekly_task.content = weekly_task.content
        old_weekly_task.is_important = weekly_task.is_important
        old_weekly_task.the_time = weekly_task.the_time
        session.commit()
        return True, weekly_task


def make_task(task: Task, user: User, session: Session) -> bool:
    """Make a task, used by the generate_tasks function"""
    user_tasks_query = session.query(Task).filter_by(owner_id=user.id)
    task_exist = user_tasks_query.filter_by(date_time=task.date_time, title=task.title).first()
    if not task_exist:
        session.add(task)
        session.commit()
        return True
    return False


def generate_tasks(session: Session, user: User):
    """Generates tasks for the week
    based on all the weekly tasks the user have"""
    current_date = date.today()
    current_week_num = current_date.strftime("%W")
    current_year = current_date.strftime("%Y")

    for weekly_task in user.weekly_tasks:
        the_time = weekly_task.the_time
        days = weekly_task.days.split(", ")
        for day in days:
            date_string = f"{day} {the_time} {current_week_num} {current_year}"
            date_time = datetime.strptime(date_string, "%a %H:%M %W %Y")
            task = Task(
                title=weekly_task.title,
                content=weekly_task.content,
                is_done=False,
                is_important=weekly_task.is_important,
                date_time=date_time,
                owner_id=user.id
            )
            make_task(task, user, session)


def remove_weekly_task(weekly_task_id: int, session: Session) -> bool:
    """Removes a weekly task from the db based on the weekly task id"""
    weekly_task = session.query(WeeklyTask).filter_by(id=weekly_task_id).first()
    if weekly_task:
        session.query(WeeklyTask).filter_by(id=weekly_task_id).delete()
        session.commit()
        return True
    return False