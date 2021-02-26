import json
from datetime import date, time

import pytest
from fastapi import status
from sqlalchemy.orm.exc import NoResultFound

from app.database.models import Task
from app.internal.todo_list import by_id
from app.internal.utils import create_model, delete_instance
from app.routers.todo_list import router

DATE = date(2021, 2, 2)
TIME = time(20, 0)
TIME2 = time(21, 0)


@pytest.fixture
def task1(session, user):
    task_example = create_model(
        session,
        Task,
        title="Test",
        description="test my create",
        is_done=False,
        is_important=False,
        date=DATE,
        time=TIME,
        owner_id=1,
        owner=user,
    )
    yield task_example
    delete_instance(session, task_example)


@pytest.fixture
def task2(session, user):
    task_example = create_model(
        session,
        Task,
        title="Test2",
        description="test my create2",
        is_done=False,
        is_important=True,
        date=DATE,
        time=TIME2,
        owner_id=1,
        owner=user,
    )
    yield task_example
    delete_instance(session, task_example)


def test_if_task_deleted(home_test_client, task1: Task, session):
    response = home_test_client.post(
        router.url_path_for('delete_task'),
        data={"task_id": task1.id},
    )
    assert response.status_code == status.HTTP_302_FOUND
    with pytest.raises(NoResultFound):
        by_id(session, task1.id)


def test_if_task_created(home_test_client, session, task1: Task, user):
    response = home_test_client.post(
        router.url_path_for('add_task'),
        data={
            "title": task1.title,
            "description": task1.description,
            "date_str": task1.date.strftime('%Y-%m-%d'),
            "time_str": task1.time.strftime('%H:%M'),
            "is_important": task1.is_important,
            "session": session
        },
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    task_ex = by_id(session, task1.id)
    assert task1 == task_ex


def test_if_task_edited(home_test_client, session, task1: Task, task2):
    response = home_test_client.post(
        router.url_path_for('edit_task'),
        data={
            "task_id": task1.id,
            "title": task2.title,
            "description": task2.description,
            "date_str": task2.date.strftime('%Y-%m-%d'),
            "time_str": task2.time.strftime('%H:%M:%S'),
            "is_important": task2.is_important,
            "session": session
        },
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    session.refresh(task1)
    assert task2.title == task1.title
    assert task2.description == task1.description
    assert task2.time == task1.time
    assert task2.is_important == task1.is_important


def test_if_task_has_done(home_test_client, session, task1: Task):
    response = home_test_client.post(
        router.url_path_for('set_task_done', task_id=task1.id),
        data={"task_id": task1.id},
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    response = home_test_client.get(
        router.url_path_for('get_task', task_id=task1.id),
    )
    content = response.content.decode('utf-8')
    content = json.loads(content)
    assert content['is_done'] is True


def test_if_task_has_not_done(home_test_client, session, task1: Task):
    response = home_test_client.post(
        router.url_path_for('set_task_undone', task_id=task1.id),
        data={
            "task_id": task1.id,
            "session": session
        },
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    response = home_test_client.get(
        router.url_path_for('get_task', task_id=task1.id),
    )
    content = response.content.decode('utf-8')
    content = json.loads(content)
    assert content['is_done'] is False
