import datetime

import pytest
from app.database.database import Base, SessionLocal, engine
from app.database.models import Event, User
from app.main import app
from faker import Faker
from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, SessionLocal, engine
from app.database.models import User
from app.routers import profile


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine)


def get_test_db():
    return TestingSessionLocal()


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


def session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def get_test_placeholder_user():
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture
def profile_test_client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[profile.get_db] = get_test_db
    app.dependency_overrides[
        profile.get_placeholder_user] = get_test_placeholder_user

    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}
