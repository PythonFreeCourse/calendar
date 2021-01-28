import pytest

from app.database.models import WeeklyTask


@pytest.fixture
def weekly_task():
    return WeeklyTask(
        title="Test Task 1",
        days="Sun, Mon, Sat",
        content="my content",
        is_important=True,
        the_time="11:00"
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