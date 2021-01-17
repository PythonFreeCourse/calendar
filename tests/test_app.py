from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.main import app, check_validation, get_db

client = TestClient(app)
date_test_data = [(datetime.today() - timedelta(1), datetime.today())]
event_test_data = [(
    {'title': "Test Title",
    "location": "Fake City",
    "from_date": date_test_data[0][0],
    "to_date": date_test_data[0][1],
    "link_vc": "https://fakevclink.com",
    "content": "Any Words",
    "repeated_event": "Onetime"},
    123,
    get_db() 
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


@pytest.mark.parametrize('values,user_id,db', event_test_data)
def test_add_event(values: dict, user_id: int, db):
    assert len(values) == len(event_test_data[0][0])
    assert user_id == 123
    assert db is not None

