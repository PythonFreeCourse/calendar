from app.database.models import WeeklyTask
from app.routers.weekly_tasks import get_placeholder_user


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
        '/weekly-tasks/execute', data=weekly_task_data).content
    # on failed attempt returns to add page
    assert b'Add Weekly Tasks' in data
    assert b'could not add The Weekly Task' in data

    # sets successful weekly task input
    # Sets the input to add mode
    input_weekly_task['mode'] = 'add'
    input_weekly_task['weekly_task_id'] = '0'
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/execute', data=input_weekly_task).content

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
    session, input_weekly_task
):
    # Get weekly tasks id from db for edit
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    w_task_id = weekly_task_from_db.id

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
        '/weekly-tasks/execute', data=input_weekly_task).content
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
        '/weekly-tasks/execute', data=input_weekly_task).content

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


def test_delete_weekly_tasks(
    weekly_tasks_test_client, session,
    input_weekly_task, weekly_task
):
    # adds weekly_task
    input_weekly_task['mode'] = 'add'
    input_weekly_task['weekly_task_id'] = '0'
    data = weekly_tasks_test_client.post(
        '/weekly-tasks/execute', data=input_weekly_task).content

    # get weekly task id for removal
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    w_task_id = weekly_task_from_db.id

    # removes weekly_task
    weekly_tasks_test_client.delete(
        f'/weekly-tasks/?remove_id={w_task_id}')

    # Checking if removed successfully
    w_task_query = session.query(WeeklyTask)
    w_task_by_title = w_task_query.filter_by(title=weekly_task.title)
    weekly_task_from_db = w_task_by_title.first()
    data = weekly_tasks_test_client.get('/weekly-tasks').content
    assert b'Weekly Tasks' in data
    assert weekly_task_from_db is None
    assert weekly_task.title.encode() not in data
