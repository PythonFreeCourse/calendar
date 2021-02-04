import pytest
from datetime import datetime

from app.database.models import WeeklyTask


@pytest.fixture
def weekly_task():
    return WeeklyTask(
        title="Test Task 1",
        days="Mon, Sat, Sun",
        content="my content",
        is_important=True,
        the_time="11:00"
    )


@pytest.fixture
def weekly_task2():
    return WeeklyTask(
        title="Test Task 2",
        days="Sat, Sun",
        content="my content2",
        is_important=False,
        the_time="12:00"
    )


@pytest.fixture
def weekly_task3():
    return WeeklyTask(
        title="Test Task 2",
        days="Sat",
        content="my content3",
        is_important=False,
        the_time="12:00"
    )


@pytest.fixture
def input_weekly_task():
    return {
        'title': 'Test Task 1',
        'sun': True,
        'mon': True,
        'sat': True,
        'content': 'my content',
        'is_important': True,
        'the_time': '11:00'
        }


@pytest.fixture
def weekly_task_time(weekly_task):
    date_time_string = f"2021-01-28 {weekly_task.the_time}"
    date_time_format = "%Y-%m-%d %H:%M"
    date_time = datetime.strptime(date_time_string, date_time_format)
    the_time = date_time.time()
    return the_time


def get_from_db(my_session, title=None):
    while True:
        if title:
            w_task_query = my_session.query(WeeklyTask)
            w_task_by_title = w_task_query.filter_by(title=title)
            weekly_task_from_db = w_task_by_title.first()
            yield weekly_task_from_db
        else:
            yield None


@pytest.fixture
def weekly_task_from_db_gen():
    return get_from_db


def get_weekly_task_id(
    from_db_gen,
    my_session,
    title
):
    while True:
        get_title_from_db = from_db_gen(
            my_session, title=title)
        w_task_from_db = next(get_title_from_db)
        if w_task_from_db:
            w_task_id = w_task_from_db.id
            yield w_task_id
        else:
            yield None


@pytest.fixture
def weekly_task_id_gen():
    return get_weekly_task_id
