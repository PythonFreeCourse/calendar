import datetime

import pytest
from app.database.database import Base, SessionLocal, engine
from app.database.models import Event, User
from app.main import app
from faker import Faker
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sessions():
    Base.metadata.create_all(bind=engine)
    sessions = SessionLocal()
    yield sessions


@pytest.fixture
def user(sessions):
    faker = Faker()
    user1 = User(username=faker.first_name(), email=faker.email())
    sessions.add(user1)
    sessions.commit()
    yield user1
    sessions.delete(user1)
    sessions.commit()


@pytest.fixture
def event(sessions, user):
    event1 = Event(title="Test Email", content="Test TEXT",
                   date=datetime.datetime.now(), owner_id=user.id)
    sessions.add(event1)
    sessions.commit()
    yield event1
    sessions.delete(event1)
    sessions.commit()
