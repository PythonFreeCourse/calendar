from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.routers.event import add_event, check_validation
from app.database.database import get_db

client = TestClient(app)

def db():
    for i in get_db():
        my_db = i
    return my_db

date_test_data = [datetime.today() - timedelta(1), datetime.today()]

event_test_data = [(
        {'title': "Test Title",
        "location": "Fake City",
        "start_date": date_test_data[0],
        "end_date": date_test_data[1],
        "vc_link": "https://fakevclink.com",
        "content": "Any Words",
        "owner_id": 123},
        db()
    )]



@pytest.fixture
def start_time():
    return date_test_data[0]
            
@pytest.fixture
def end_time():
    return date_test_data[1]

def test_read_main():
    response = client.get("/")
    assert response.ok


def test_session_db():
    assert get_db() is not None


def test_get_profile():
    response = client.get("/profile/123/EditEvent")
    assert response.ok

def test_check_validation():
    assert check_validation(1, 2)


@pytest.mark.parametrize('values,db', event_test_data)
def test_add_event(values: dict, db):
    assert db is not None
    assert add_event(values, db) is not None


def test_get_editevent_page():
    response = client.get("/profile/122/EditEvent")
    assert response.ok
    assert b'Time range' in response.content


def test_post_editevent():
    response = client.post(
        "/profile/123/EditEvent",
        headers={"X-Token": "coneofsilence"},
        data={"user_id": 123,
            'event_title': "Title",
            "from_date": date_test_data[0],
            "to_date": date_test_data[1]}
    )
    assert response.ok


