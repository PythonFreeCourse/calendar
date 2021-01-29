from datetime import datetime, time

from app.database.models import WeeklyTask, Task, User
from app.routers.weekly_tasks import get_placeholder_user
from app.internal.weekly_tasks import check_inputs, generate_tasks
from app.internal.weekly_tasks import make_or_change_weekly_task, make_task
from app.internal.weekly_tasks import remove_weekly_task


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
    # Get weekly-tasks/add page
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
    # Checks that all weekly task details are displayed
    assert b'Weekly Tasks' in data
    assert weekly_task.title.encode() in data
    assert weekly_task.days.encode() in data
    assert weekly_task.content.encode() in data
    assert weekly_task.the_time.encode() in data


def test_weekly_tasks_edit(
    weekly_tasks_test_client, weekly_task,
    session, input_weekly_task
):
    # Get weekly tasks from db for edit
    w_t = session.query(WeeklyTask).filter_by(title=weekly_task.title).first()
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/edit', data={"edit_id": w_t.id}).content

    # Checks that all weekly task details are displayed
    assert b'Edit Weekly Tasks' in data
    assert weekly_task.title.encode() in data
    assert weekly_task.content.encode() in data
    assert weekly_task.the_time.encode() in data

    # Sets the input to edit mode
    input_weekly_task['mode'] = 'edit'
    # Sets the id for edit
    input_weekly_task['weekly_task_id'] = w_t.id

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
    input_weekly_task, weekly_task
):
    # adds weekly_task
    input_weekly_task['mode'] = 'add'
    input_weekly_task['weekly_task_id'] = '0'
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/make-change', data=input_weekly_task).content

    # Checking if added successfully
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    w_t = session.query(WeeklyTask).filter_by(title=weekly_task.title).first()
    assert b'Weekly Tasks' in data
    assert w_t.title == weekly_task.title
    assert weekly_task.title.encode() in data

    # removes weekly_task
    weekly_tasks_test_client.post(
        '/weekly-tasks/remove', data={'remove_id': w_t.id})

    # Checking if removed successfully
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    w_t = session.query(WeeklyTask).filter_by(title=weekly_task.title).first()
    assert b'Weekly Tasks' in data
    assert w_t is None
    assert weekly_task.title.encode() not in data


def test_internal_weekly_tasks_check_inputs():
    the_time = time(1, 1, 1)
    ok = check_inputs(days="", the_time=None, title="the title")
    assert not ok
    ok = check_inputs(days="Sun", the_time=the_time, title="the title")
    assert ok


def test_internal_weekly_tasks_make_task(user, session):
    made_user = session.query(User).filter_by(username=user.username).first()
    date_time = datetime(2021, 1, 21, 3, 19)
    task = Task(
        title="task1",
        content="my content",
        is_done=False,
        is_important=True,
        date_time=date_time,
        owner_id=made_user.id
    )
    made = make_task(task, user, session)
    assert made
    made = make_task(task, user, session)
    assert not made

    made_task = session.query(Task).filter_by(title="task1").first()
    assert made_task.date_time == date_time


def test_internal_weekly_tasks_make_or_change_weekly_task(
    user,
    session,
    weekly_task
):
    # seting the time
    date_string = f"2021-01-28 {weekly_task.the_time}"
    date_format = "%Y-%m-%d %H:%M"
    date_time = datetime.strptime(date_string, date_format)
    the_time = date_time.time()

    # When unable to create the weekly task
    made, w_t = make_or_change_weekly_task(
        user,
        session,
        mode="add",
        weekly_task_id=0,
        title=None,
        days=weekly_task.days,
        content=weekly_task.content,
        is_important=weekly_task.is_important,
        the_time=the_time
    )
    assert not made
    # As much data as possible is saved, except for time and days
    assert w_t.content == weekly_task.content
    assert w_t.days != weekly_task.days
    assert w_t.the_time != weekly_task.the_time

    # When successful on making the weekly task
    made, w_t = make_or_change_weekly_task(
        user,
        session,
        mode="add",
        weekly_task_id=0,
        title=weekly_task.title,
        days=weekly_task.days,
        content=weekly_task.content,
        is_important=weekly_task.is_important,
        the_time=the_time
    )
    assert made

    # the weekly task added to the db and successfully saved the data
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    assert weekly_task_from_db
    assert weekly_task_from_db.content == weekly_task.content
    assert weekly_task_from_db.the_time == weekly_task.the_time

    # with the id of the weekly task we edit it
    edit_id = weekly_task_from_db.id
    made, w_t = make_or_change_weekly_task(
        user, session,
        mode="edit",
        weekly_task_id=edit_id,
        title="new title",
        days=weekly_task.days,
        content="new content",
        is_important=weekly_task.is_important,
        the_time=the_time
    )
    assert made
    w_task_query = session.query(WeeklyTask)
    w_task_by_id = w_task_query.filter_by(id=edit_id)
    edited_w_t_from_db = w_task_by_id.first()
    assert edited_w_t_from_db.content == "new content"
    assert edited_w_t_from_db.title == "new title"


def test_internal_weekly_tasks_remove_weekly_task(user, session, weekly_task):
    # seting the time and making the weekly task
    date_time_string = f"2021-01-28 {weekly_task.the_time}"
    date_time_format = "%Y-%m-%d %H:%M"
    date_time = datetime.strptime(date_time_string, date_time_format)
    the_time = date_time.time()
    made, _ = make_or_change_weekly_task(
        user,
        session,
        mode="add",
        weekly_task_id=0,
        title=weekly_task.title,
        days=weekly_task.days,
        content=weekly_task.content,
        is_important=weekly_task.is_important,
        the_time=the_time
    )
    assert made

    # Checks if the weekly task exists in the db
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    assert weekly_task_from_db
    # geting the id of the weekly task to remove it
    weekly_task_id = weekly_task_from_db.id
    removed = remove_weekly_task(weekly_task_id, session)
    assert removed
    # Checks if the weekly task exists in the db after removal
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    assert not weekly_task_from_db

    # Trying to remove a weekly task that does not exists
    removed = remove_weekly_task(weekly_task_id, session)
    assert not removed


def test_internal_weekly_tasks_generate_tasks(user, session, weekly_task):
    # seting the time and making the weekly task
    date_time_string = f"2021-01-28 {weekly_task.the_time}"
    date_time_format = "%Y-%m-%d %H:%M"
    date_time = datetime.strptime(date_time_string, date_time_format)
    the_time = date_time.time()
    made, _ = make_or_change_weekly_task(
        user,
        session,
        mode="add",
        weekly_task_id=0,
        title=weekly_task.title,
        days=weekly_task.days,
        content=weekly_task.content,
        is_important=weekly_task.is_important,
        the_time=the_time
    )
    assert made

    # Activates the function
    generate_tasks(session, user)

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
    generate_tasks(session, user)
    tasks = user.tasks
    assert len(tasks) == 3
