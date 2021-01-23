from fastapi.testclient import TestClient
import pytest

from app.database.models import User
from app.main import app
from app.database.database import Base
from app.routers import profile, agenda, invitation, event
from tests.conftest import test_engine, get_test_db


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def event_test_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[event.get_db] = get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


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
