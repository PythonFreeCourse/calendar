from datetime import date, datetime, time

from app.database.models import User, Task, WeeklyTask
from sqlalchemy.orm.session import Session


def check_inputs(days: str, the_time: time, title: str) -> bool:
    """Checks inputs, used by the get_w_t_from_input function"""
    if not days or not the_time or not title:
        return False
    return True


def get_w_t_from_input(
    user: User,
    title: str, days: str,
    content: str, the_time: time,
    is_important: bool,
    weekly_task_id: int = 0
) -> WeeklyTask:
    """This function is being used to make a Weekly Task model
        from the inputs.

    Args:
        user (User): The user who wants to make or edit a Weekly Task.
        title (str): Title of the Weekly Task.
        days (str): Return days of the Weekly Task.
        content (str): Content of the Weekly Task.
        the_time (time): Return time of the Weekly Task.
        is_important (bool): If the task is important.
        weekly_task_id (int): The id of the weekly task, zero if not mentioned.

    Returns:
        WeeklyTask: the model WeeklyTask which the function managed to make.
    """
    weekly_task = WeeklyTask(
        title=title,
        content=content,
        is_important=is_important,
        owner_id=user.id
    )

    if weekly_task_id != 0:
        weekly_task.id = weekly_task_id

    inputs_ok = check_inputs(days, the_time, title)
    if not inputs_ok:
        return weekly_task
    weekly_task.days = days
    weekly_task.the_time = the_time.strftime("%H:%M")
    return weekly_task


def make_weekly_task(
    user: User, session: Session,
    weekly_task: WeeklyTask
) -> bool:
    """This function is being used to add a Weekly Task to the user.

        Args:
            user (User): The user who wants to add the Weekly Task.
            session (Session): The session to redirect to the database.
            weekly_task (WeeklyTask): The Weekly Task that the user will add.

        Returns:
            bool: Shows if the weekly_task has been added to the db.
        """
    if weekly_task.days is None or weekly_task.the_time is None:
        return False
    user_titles = (
        user_weekly_task.title
        for user_weekly_task in user.weekly_tasks
    )
    if weekly_task.title in user_titles:
        return False
    session.add(weekly_task)
    session.commit()
    return True


def change_weekly_task(
    user: User, session: Session,
    weekly_task: WeeklyTask
) -> bool:
    """This function is being used to edit a Weekly Task the user have.

        Args:
            user (User): The user who wants to edit the Weekly Task.
            session (Session): The session to redirect to the database.
            weekly_task (WeeklyTask): The Weekly Task that the of the user,
                with the edited values.

        Returns:
            bool: Shows if the weekly_task has been edited in the db.
        """
    if weekly_task.days is None or weekly_task.the_time is None:
        return False
    w_task_query = session.query(WeeklyTask)
    old_weekly_task = w_task_query.filter_by(id=weekly_task.id).first()

    user_titles = (
        user_weekly_task.title for user_weekly_task in user.weekly_tasks
        if user_weekly_task.title != old_weekly_task.title
    )

    if weekly_task.title in user_titles:
        return False

    if weekly_task.owner_id != user.id:
        return False

    old_weekly_task.title = weekly_task.title
    old_weekly_task.days = weekly_task.days
    old_weekly_task.content = weekly_task.content
    old_weekly_task.is_important = weekly_task.is_important
    old_weekly_task.the_time = weekly_task.the_time
    session.commit()
    return True


def make_task(task: Task, user: User, session: Session) -> bool:
    """Make a task, used by the generate_tasks function"""
    user_tasks_query = session.query(Task).filter_by(owner_id=user.id)
    task_by_time = user_tasks_query.filter_by(date_time=task.date_time)
    task_by_title_and_time = task_by_time.filter_by(title=task.title)
    task_exist = task_by_title_and_time.first()
    if task_exist:
        return False
    session.add(task)
    session.commit()
    return True


def get_datetime(day, the_time):
    """Getting the datetime of days in the current week,
    used by the generate_tasks function"""
    current_date = date.today()
    current_week_num = current_date.strftime("%W")
    current_year = current_date.strftime("%Y")
    date_string = f"{day} {the_time} {current_week_num} {current_year}"
    return datetime.strptime(date_string, "%a %H:%M %W %Y")


def generate_tasks(session: Session, user: User):
    """Generates tasks for the week
    based on all the weekly tasks the user have"""
    for weekly_task in user.weekly_tasks:
        the_time = weekly_task.the_time
        days = weekly_task.days.split(", ")
        for day in days:
            date_time = get_datetime(day, the_time)
            task = Task(
                title=weekly_task.title,
                content=weekly_task.content,
                is_done=False,
                is_important=weekly_task.is_important,
                date_time=date_time,
                owner_id=user.id
            )
            yield make_task(task, user, session)
    yield False


def remove_weekly_task(weekly_task_id: int, session: Session) -> bool:
    """Removes a weekly task from the db based on the weekly task id"""
    weekly_task_query = session.query(WeeklyTask)
    weekly_task = weekly_task_query.filter_by(id=weekly_task_id).first()
    if not weekly_task:
        return False
    session.query(WeeklyTask).filter_by(id=weekly_task_id).delete()
    session.commit()
    return True
