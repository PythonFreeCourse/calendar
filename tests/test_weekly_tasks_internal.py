from datetime import datetime

from app.database.models import Task
from app.internal.weekly_tasks import (
    check_inputs,
    generate_tasks,
    create_task,
    remove_weekly_task,
    weekly_task_from_input,
    create_weekly_task,
    change_weekly_task,
)


def test_weekly_tasks_check_inputs(weekly_task_time):
    ok = check_inputs(days="", task_time=None, title="the title")
    assert not ok
    ok = check_inputs(
        days="Sun",
        task_time=weekly_task_time,
        title="the title",
    )
    assert ok


def test_weekly_tasks_create_task(user, session):
    date_time = datetime(2021, 1, 21, 3, 19)
    task = Task(
        title="task1",
        description="my description",
        is_done=False,
        is_important=True,
        date=date_time.date(),
        time=date_time.time(),
        owner_id=user.id,
    )
    created = create_task(task, user, session)
    assert created
    created = create_task(task, user, session)
    assert not created
    created_task = user.tasks[0]
    assert created_task.date == date_time.date()
    assert created_task.time == date_time.time()


def test_create_weekly_task(user, session, weekly_task):
    # creating the weekly task
    weekly_task.user_id = user.id
    created = create_weekly_task(weekly_task, session)
    assert created
    # checks if weekly task been added to the db
    user_w_t = user.weekly_tasks[0]
    assert user_w_t
    assert user_w_t.content == weekly_task.content
    assert user_w_t.task_time == weekly_task.task_time

    # adding without a title
    weekly_task.title = None
    created = create_weekly_task(weekly_task, session)
    assert not created

    # the user's weekly tasks should remain in quantity 1
    user_w_tasks = user.weekly_tasks
    assert len(user_w_tasks) == 1


def test_change_weekly_task(
    user,
    session,
    weekly_task,
    weekly_task2,
    weekly_task3,
):
    # creating weekly task for edit testing
    weekly_task.user_id = user.id
    created = create_weekly_task(weekly_task, session)
    assert created

    # creating another weekly task for edit testing
    weekly_task2.user_id = user.id
    created = create_weekly_task(weekly_task2, session)
    assert created
    user_w_t = user.weekly_tasks
    assert len(user_w_t) == 2

    # get weekly task id for edit
    user_w_t = user.weekly_tasks[0]
    edit_id = user_w_t.id

    # seting the weekly task for editing
    weekly_task.id = edit_id
    weekly_task.title = "new title"
    weekly_task.content = "new content"

    changed = change_weekly_task(user, weekly_task, session)
    assert changed
    changed_user_w_t = user.weekly_tasks[0]
    assert changed_user_w_t.title == weekly_task.title
    assert changed_user_w_t.content == weekly_task.content

    # editing without a title
    weekly_task3.user_id = user.id
    weekly_task3.id = edit_id
    weekly_task3.title = None
    changed = change_weekly_task(user, weekly_task3, session)
    assert not changed
    edited_w_t = user.weekly_tasks[0]
    assert edited_w_t.title != weekly_task3.title


def test_weekly_task_change_permission(
    user,
    user2,
    session,
    weekly_task,
    weekly_task2,
):
    # creating the weekly task
    weekly_task.user_id = user.id
    created = create_weekly_task(weekly_task, session)
    assert created
    user_w_task = user.weekly_tasks[0]
    assert user_w_task

    # another user trying to change the weekly task
    weekly_task2.id = user_w_task.id
    weekly_task2.user_id = user2.id
    changed = change_weekly_task(user2, weekly_task, session)
    assert not changed
    user_w_t = user.weekly_tasks[0]
    assert user_w_t.title != weekly_task2.title
    assert user_w_t.content != weekly_task2.content
    assert user_w_t.is_important != weekly_task2.is_important


def test_weekly_task_from_input(user, weekly_task, weekly_task_time):
    # all inputs are ok
    w_t = weekly_task_from_input(
        user,
        weekly_task.title,
        weekly_task.get_days(),
        weekly_task.content,
        weekly_task_time,
        weekly_task.is_important,
        weekly_task_id=1,
    )
    assert w_t
    # all the weekly task data should be saved
    assert w_t.title == weekly_task.title
    assert w_t.days == weekly_task.days
    assert w_t.content == weekly_task.content
    assert w_t.is_important == weekly_task.is_important
    assert w_t.task_time == weekly_task.task_time

    # not all inputs are ok
    w_t = weekly_task_from_input(
        user,
        "",
        weekly_task.days,
        weekly_task.content,
        weekly_task_time,
        weekly_task.is_important,
    )
    assert w_t
    # As much data as possible is saved, except for time and days
    assert w_t.content == weekly_task.content
    assert w_t.days != weekly_task.days
    assert w_t.task_time != weekly_task.task_time


def test_remove_weekly_task(user, session, weekly_task):
    weekly_task.user_id = user.id
    created = create_weekly_task(weekly_task, session)
    assert created

    # Checks if the weekly task exists in the db
    user_w_task = user.weekly_tasks[0]
    assert user_w_task
    # geting the id of the weekly task for removal
    weekly_task_id = user_w_task.id
    removed = remove_weekly_task(weekly_task_id, session)
    assert removed
    # Checks if the weekly task exists in the db after removal
    assert not user.weekly_tasks

    # Trying to remove a weekly task that does not exists
    removed = remove_weekly_task(weekly_task_id, session)
    assert not removed


def test_weekly_tasks_generate_tasks(user, session, weekly_task):
    weekly_task.user_id = user.id
    created = create_weekly_task(weekly_task, session)
    assert created

    # Activates the generator
    task_gen = generate_tasks(user, session)
    tasks_added = list(task_gen)

    # the number of days defined in the weekly task is 3
    assert tasks_added.count(True) == 3

    tasks = user.tasks
    # The number of tasks a user has should be
    # the number of days defined in the weekly task
    assert len(tasks) == 3
    # The Tasks should be defined according to the weekly task
    for task in tasks:
        assert weekly_task.title == task.title
        assert weekly_task.content == task.description
        assert weekly_task.is_important == task.is_important
        time_string = task.time.strftime("%H:%M")
        assert weekly_task.task_time == time_string
        day = task.date.strftime("%a")
        assert day in weekly_task.get_days()

    # another activation at the same day
    # shouldn't affect the db
    # Only after a week new tasks should be added
    task_gen = generate_tasks(user, session)
    tasks_added = list(task_gen)
    assert tasks_added.count(True) == 0
    tasks = user.tasks
    assert len(tasks) == 3
