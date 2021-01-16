import datetime

import pytest
from app.database.database import Base, SessionLocal, engine
from app.database.models import Event, User
from app.main import app
from faker import Faker
from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis.strategies import emails


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sessions():
    Base.metadata.create_all(bind=engine)
    sessions = SessionLocal()
    yield sessions
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
@given(email=emails())
def user(sessions, email):
    faker1 = Faker()
    User1 = User(username=faker1.first_name(), email=email)
    sessions.add(User1)
    sessions.commit()


@pytest.fixture
def event(sessions, user):
    Event1 = Event(title="Test Email", content="Test TEXT",
                   date=datetime.datetime.now(), owner_id=user.id)
    sessions.add(Event1)
    sessions.commit()
