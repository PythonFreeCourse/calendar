from typing import Iterator

from fastapi.testclient import TestClient
import pytest

from app.database.models import Base, User
from app import main
from app.routers import agenda, event, invitation, profile
from app.routers.salary import routes as salary
from tests.conftest import get_test_db, test_engine


def get_test_placeholder_user() -> Iterator[User]:
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    return TestClient(main.app)


def create_test_client(get_db_function) -> Iterator[TestClient]:
    Base.metadata.create_all(bind=test_engine)
    main.app.dependency_overrides[get_db_function] = get_test_db

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def agenda_test_client() -> Iterator[TestClient]:
    yield from create_test_client(agenda.get_db)


@pytest.fixture(scope="session")
def event_test_client() -> Iterator[TestClient]:
    yield from create_test_client(event.get_db)


@pytest.fixture(scope="session")
def home_test_client() -> Iterator[TestClient]:
    yield from create_test_client(main.get_db)


@pytest.fixture(scope="session")
def invitation_test_client() -> Iterator[TestClient]:
    yield from create_test_client(invitation.get_db)


@pytest.fixture(scope="session")
def profile_test_client() -> Iterator[TestClient]:
    Base.metadata.create_all(bind=test_engine)
    main.app.dependency_overrides[profile.get_db] = get_test_db
    main.app.dependency_overrides[
        profile.get_placeholder_user] = get_test_placeholder_user

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def salary_test_client() -> Iterator[TestClient]:
    yield from create_test_client(salary.get_db)
