import pytest
from app.database.database import Base
from app.database.models import User
from app.main import app
from app.routers import agenda, audio, invitation, profile
from fastapi.testclient import TestClient

from tests.conftest import get_test_db, test_engine


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def agenda_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[agenda.get_db] = get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def invitation_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[invitation.get_db] = get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


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
        full_name='FakeName'
    )


def get_test_placeholder_user2():
    return User(
        username='new_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture
def audio_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[audio.get_db] = get_test_db
    app.dependency_overrides[
        audio.get_placeholder_user] = get_test_placeholder_user2
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}