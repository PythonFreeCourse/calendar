from fastapi.testclient import TestClient
import pytest

from app import main
from app.database.database import Base
from app.database.models import User
from app.main import app
from app.routers import agenda, audio, event, invitation, profile
from tests.conftest import get_test_db, test_engine


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def create_test_client(get_db_function):
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db_function] = get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def agenda_test_client():
    yield from create_test_client(agenda.get_db)


@pytest.fixture(scope="session")
def invitation_test_client():
    yield from create_test_client(invitation.get_db)


@pytest.fixture(scope="session")
def home_test_client():
    yield from create_test_client(main.get_db)


@pytest.fixture(scope="session")
def event_test_client():
    yield from create_test_client(event.get_db)


@pytest.fixture(scope="session")
def profile_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[profile.get_db] = get_test_db
    app.dependency_overrides[
        profile.get_placeholder_user] = get_test_placeholder_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


def get_test_placeholder_user():
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName',
        language_id=1,
        telegram_id='666666'
    )


def get_test_placeholder_user2():
    return User(
        username='new_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture(scope="session")
def audio_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[audio.get_db] = get_test_db
    app.dependency_overrides[
        audio.get_placeholder_user] = get_test_placeholder_user2
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=test_engine)
