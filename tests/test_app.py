from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.main import add_event, app, check_validation, get_db

client = TestClient(app)
date_test_data = [(datetime.today() - timedelta(1), datetime.today())]
event_test_data = [(
    {'title': "Test Title",
    "location": "Fake City",
    "start_date": date_test_data[0][0],
    "end_date": date_test_data[0][1],
    "vc_link": "https://fakevclink.com",
    "content": "Any Words",
    "owner_id": 123},
    get_db
)]


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_session_db():
    assert get_db() is not None


def test_get_profile():
    response = client.get("/profile/123/EditEvent")
    assert response.status_code == 200


@pytest.mark.parametrize('start_time,end_time', date_test_data)
def test_check_validation(start_time, end_time):
    assert check_validation(start_time, end_time)


@pytest.mark.parametrize('values,db', event_test_data)
def test_add_event(values: dict, db):
    assert len(values) == len(event_test_data[0][0])
    assert db is not None
    assert add_event(event_test_data[0][0], db) is not None


def test_get_editevent_page():
    response = client.get("/profile/122/EditEvent")
    assert response.status_code == 200
    assert b'Time range' in response.content

def test_post_editevent():
    response = client.post(
        "/profile/123/EditEvent",
        headers={"X-Token": "coneofsilence"},
        data={"user_id": 123,
            'event_title': "Title",
            "from_date": date_test_data[0][1],
            "to_date": date_test_data[0][1]}
    )
    assert response.status_code == 200


