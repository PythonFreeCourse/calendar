import pytest
<<<<<<< HEAD
from app.database.database import Base, SessionLocal, engine
from app.database.models import AudioSettings, Event, User
from app.main import app
from app.routers import audio, profile
from faker import Faker
from fastapi.testclient import TestClient
=======
>>>>>>> 0b4570bb088c75e6d1848f1eadefd7f190dab1c2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.invitation_fixture',
    'tests.association_fixture',
    'tests.client_fixture',
    'smtpdfix',
]

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine)


def get_test_db():
    return TestingSessionLocal()


@pytest.fixture
def session():
    Base.metadata.create_all(bind=test_engine)
    session = get_test_db()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)
<<<<<<< HEAD
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[profile.get_db] = get_test_db
    app.dependency_overrides[
        profile.get_placeholder_user] = get_test_placeholder_user

    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture
def audio_test_client(session):
    app.dependency_overrides[audio.get_db] = get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}
=======
>>>>>>> 0b4570bb088c75e6d1848f1eadefd7f190dab1c2
