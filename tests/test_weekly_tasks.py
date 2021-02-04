from datetime import datetime

from app.database.models import Task
from app.routers.weekly_tasks import get_placeholder_user
from app.internal.weekly_tasks import (
    check_inputs, generate_tasks, create_task, remove_weekly_task,
    weekly_task_from_input, create_weekly_task, change_weekly_task
)


def test_get_placeholder_user():
    user = get_placeholder_user()
    assert user.username == 'demo_user'
    assert user.email == 'demo@email.po'
    assert user.password == 's3jsd183b13'
    assert user.full_name == 'The Demo'


def test_weekly_tasks_manager(weekly_tasks_test_client):
    # Get weekly-tasks page
    data = weekly_tasks_test_client.get('/weekly-tasks').content

    # Verify that it is the page and there are no tasks
    assert b'Weekly Tasks' in data
    assert b'Test Task 1' not in data


def test_weekly_tasks_add(
    weekly_tasks_test_client,
    weekly_task, input_weekly_task
):
    # Get add page
    data = weekly_tasks_test_client.get('/weekly-tasks/add').content
    # Verify that it is the add page
    assert b'Add Weekly Tasks' in data

    # set weekly task data for failed attempt
    weekly_task_data = {
        'title': weekly_task.title,
        'mode': 'add',
        'weekly_task_id': '0'
    }
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=weekly_task_data).content
    # on failed attempt returns to add page
    assert b'Add Weekly Tasks' in data
    assert b'could not add The Weekly Task' in data

    # sets successful weekly task input
    # Sets the input to add mode
    input_weekly_task['mode'] = 'add'
    input_weekly_task['weekly_task_id'] = '0'
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=input_weekly_task).content

    # on successful attempt doesn't returns to add page
    assert b'Add Weekly Tasks' not in data

    # Get weekly-tasks manager page
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    # Checks that weekly task details are displayed
    assert b'Weekly Tasks' in data
    assert weekly_task.title.encode() in data
    assert weekly_task.days.encode() in data
    assert weekly_task.content.encode() in data
    assert weekly_task.the_time.encode() in data


def test_weekly_tasks_edit(
    weekly_tasks_test_client, weekly_task,
    session,
    input_weekly_task,
    weekly_task_from_db_gen,
    weekly_task_id_gen
):
    get_weekly_task_id = weekly_task_id_gen(
        weekly_task_from_db_gen,
        session,
        weekly_task.title
    )

    # Get weekly tasks id from db for edit
    w_task_id = next(get_weekly_task_id)

    data = weekly_tasks_test_client.post(
        '/weekly-tasks/edit',
        data={"edit_id": w_task_id}).content

    # Checks that all weekly task details are displayed
    assert b'Edit Weekly Tasks' in data
    assert weekly_task.title.encode() in data
    assert weekly_task.content.encode() in data
    assert weekly_task.the_time.encode() in data

    # Sets the input to edit mode
    input_weekly_task['mode'] = 'edit'
    # Sets the id for edit
    input_weekly_task['weekly_task_id'] = w_task_id

    # set weekly task input for failed attempt
    input_weekly_task['title'] = ""
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=input_weekly_task).content
    # on failed attempt returns to edit page
    assert b'Edit Weekly Tasks' in data
    assert b'These changes could not be made to the Weekly Task' in data
    assert weekly_task.title.encode() not in data
    assert weekly_task.content.encode() in data

    # sets successful weekly task input
    input_weekly_task['title'] = "Test Task 2"
    input_weekly_task['fri'] = True
    input_weekly_task['thu'] = True
    input_weekly_task['sun'] = False

    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=input_weekly_task).content

    # on successful attempt doesn't returns to add page
    assert b'Edit Weekly Tasks' not in data

    # Get weekly-tasks manager page
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    # Checks that all weekly task details are displayed correctly
    assert b'Weekly Tasks' in data
    assert weekly_task.title.encode() not in data
    assert b'Test Task 2' in data
    assert weekly_task.days.encode() not in data
    assert b'Mon, Thu, Fri, Sat' in data
    assert weekly_task.content.encode() in data
    assert weekly_task.the_time.encode() in data


def test_weekly_tasks_remove(
    weekly_tasks_test_client, session,
    input_weekly_task, weekly_task,
    weekly_task_from_db_gen,
    weekly_task_id_gen
):
    get_weekly_task_from_db = weekly_task_from_db_gen(
        session, title=weekly_task.title)

    get_weekly_task_id = weekly_task_id_gen(
        weekly_task_from_db_gen,
        session,
        weekly_task.title
    )

    # adds weekly_task
    input_weekly_task['mode'] = 'add'
    input_weekly_task['weekly_task_id'] = '0'
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=input_weekly_task).content

    # get weekly task id for removal
    w_task_id = next(get_weekly_task_id)

    # removes weekly_task
    weekly_tasks_test_client.post(
        '/weekly-tasks/delete',
        data={'remove_id': w_task_id})

    # Checking if removed successfully
    weekly_task_from_db = next(get_weekly_task_from_db)
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    assert b'Weekly Tasks' in data
    assert weekly_task_from_db is None
    assert weekly_task.title.encode() not in data


def test_internal_weekly_tasks_check_inputs(
    weekly_task_time
):
    ok = check_inputs(
        days="",
        the_time=None,
        title="the title")
    assert not ok
    ok = check_inputs(
        days="Sun",
        the_time=weekly_task_time,
        title="the title"
    )
    assert ok


def test_internal_weekly_tasks_create_task(user, session):
    date_time = datetime(2021, 1, 21, 3, 19)
    task = Task(
        title="task1",
        content="my content",
        is_done=False,
        is_important=True,
        date_time=date_time,
        owner_id=user.id
    )
    made = create_task(task, user, session)
    assert made
    made = create_task(task, user, session)
    assert not made
    made_task = user.tasks[0]
    assert made_task.date_time == date_time


def test_internal_create_weekly_task(
    user,
    session,
    weekly_task
):
    # When successful on making the weekly task
    weekly_task.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert made
    # the weekly task should be added to the db
    user_w_t = user.weekly_tasks[0]

    assert user_w_t
    assert user_w_t.content == weekly_task.content
    assert user_w_t.the_time == weekly_task.the_time

    # When trying to add weekly task with the same title
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert not made

    # when there is no title
    weekly_task.title = None
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert not made

    # The db user's weekly tasks should remain in quantity 1
    user_w_tasks = user.weekly_tasks
    assert len(user_w_tasks) == 1


def test_internal_change_weekly_task(
    user,
    session,
    weekly_task,
    weekly_task2,
    weekly_task3
):
    # making w_t for edit testing
    weekly_task.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert made

    # making another w_t for edit testing
    weekly_task2.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task2,
        session
    )
    assert made
    user_w_t = user.weekly_tasks
    assert len(user_w_t) == 2

    # get weekly task id for edit
    user_w_t = user.weekly_tasks[0]
    edit_id = user_w_t.id

    # seting the weekly task for editing
    weekly_task.id = edit_id
    weekly_task.title = "new title"
    weekly_task.content = "new content"

    changed = change_weekly_task(
        user,
        weekly_task,
        session
    )
    assert changed
    changed_user_w_t = user.weekly_tasks[0]
    assert changed_user_w_t.title == weekly_task.title
    assert changed_user_w_t.content == weekly_task.content

    # When trying to edit weekly task for an existing title
    # weekly_task3.title == weekly_task2.title
    weekly_task3.owner_id = user.id
    weekly_task3.id = edit_id
    changed = change_weekly_task(
        user,
        weekly_task3,
        session
    )
    assert not changed
    edited_w_t = user.weekly_tasks[0]
    assert edited_w_t.title != weekly_task3.title


def test_internal_weekly_task_change_permission(
    user,
    user2,
    session,
    weekly_task,
    weekly_task2
):
    # making the weekly task
    weekly_task.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert made
    user_w_task = user.weekly_tasks[0]
    assert user_w_task

    # another user trying to change the weekly task
    weekly_task2.id = user_w_task.id
    weekly_task2.owner_id = user2.id
    changed = change_weekly_task(
        user2,
        weekly_task,
        session
    )
    assert not changed
    user_w_t = user.weekly_tasks[0]
    assert user_w_t.title != weekly_task2.title
    assert user_w_t.content != weekly_task2.content
    assert user_w_t.is_important != weekly_task2.is_important


def test_weekly_task_from_input(user, weekly_task, weekly_task_time):
    # when all inputs are ok
    w_t = weekly_task_from_input(
        user,
        weekly_task.title,
        weekly_task.days,
        weekly_task.content,
        weekly_task_time,
        weekly_task.is_important,
        weekly_task_id=1
    )
    assert w_t
    # all the weekly task data should be saved
    assert w_t.title == weekly_task.title
    assert w_t.days == weekly_task.days
    assert w_t.content == weekly_task.content
    assert w_t.is_important == weekly_task.is_important
    assert w_t.the_time == weekly_task.the_time

    # when not all inputs are ok
    w_t = weekly_task_from_input(
        user,
        "",
        weekly_task.days,
        weekly_task.content,
        weekly_task_time,
        weekly_task.is_important
    )
    assert w_t
    # As much data as possible is saved, except for time and days
    assert w_t.content == weekly_task.content
    assert w_t.days != weekly_task.days
    assert w_t.the_time != weekly_task.the_time


def test_internal_remove_weekly_task(
    user, session,
    weekly_task
):
    weekly_task.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert made

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


def test_internal_weekly_tasks_generate_tasks(
    user, session,
    weekly_task
):
    weekly_task.owner_id = user.id
    made = create_weekly_task(
        user,
        weekly_task,
        session
    )
    assert made

    # Activates the generator
    task_gen = generate_tasks(user, session)
    tasks_added = [task_added for task_added in task_gen]

    # the number of days defined in the weekly task is 3
    assert tasks_added.count(True) == 3

    tasks = user.tasks
    # The number of tasks a user has should be
    # the number of days defined in the weekly task
    assert len(tasks) == 3
    # The Tasks should be defined according to the weekly task
    for task in tasks:
        assert weekly_task.title == task.title
        assert weekly_task.content == task.content
        assert weekly_task.is_important == task.is_important
        time_string = task.date_time.strftime("%H:%M")
        assert weekly_task.the_time == time_string
        day = task.date_time.strftime("%a")
        assert day in weekly_task.days

    # another activation at the same day
    # shouldn't affect the db
    # Only after a week new tasks should be added
    task_gen = generate_tasks(user, session)
    tasks_added = [task_added for task_added in task_gen]
    assert tasks_added.count(True) == 0
    tasks = user.tasks
    assert len(tasks) == 3
