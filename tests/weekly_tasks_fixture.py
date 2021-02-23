import pytest
from datetime import datetime

from app.database.models import WeeklyTask


@pytest.fixture
def weekly_task():
    w_t = WeeklyTask(
        title="Test Task 1",
        content="my content",
        is_important=True,
        the_time="11:00",
    )
    w_t.set_days("Mon, Sat, Sun")
    return w_t


@pytest.fixture
def weekly_task2():
    w_t = WeeklyTask(
        title="Test Task 2",
        content="my content2",
        is_important=False,
        the_time="12:00",
    )
    w_t.set_days("Sat, Sun")
    return w_t


@pytest.fixture
def weekly_task3():
    w_t = WeeklyTask(
        title="Test Task 2",
        days="Sat",
        content="my content3",
        is_important=False,
        the_time="12:00",
    )
    w_t.set_days("Sat")
    return w_t


@pytest.fixture
def input_weekly_task():
    return {
        "title": "Test Task 1",
        "sun": True,
        "mon": True,
        "sat": True,
        "content": "my content",
        "is_important": True,
        "the_time": "11:00",
    }


@pytest.fixture
def weekly_task_time(weekly_task):
    date_time_string = f"2021-01-28 {weekly_task.the_time}"
    date_time_format = "%Y-%m-%d %H:%M"
    date_time = datetime.strptime(date_time_string, date_time_format)
    the_time = date_time.time()
    return the_time
