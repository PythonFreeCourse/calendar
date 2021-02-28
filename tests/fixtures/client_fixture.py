from typing import Dict, Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import main
from app.database.models import Base, User
from app.routers import (
    agenda,
    audio,
    categories,
    dayview,
    event,
    friendview,
    google_connect,
    meds,
    notification,
    profile,
    weekview,
    weight,
)
from app.routers.salary import routes as salary
from tests import security_testing_routes
from tests.conftest import get_test_db, test_engine

LOGIN_DATA_TYPE = Dict[str, str]

main.app.include_router(security_testing_routes.router)


def login_client(client: TestClient, data: LOGIN_DATA_TYPE) -> None:
    client.post(client.app.url_path_for("login"), data=data)


def get_test_placeholder_user() -> User:
    return User(
        username="fake_user",
        email="fake@mail.fake",
        password="123456fake",
        full_name="FakeName",
        language_id=1,
        telegram_id="666666",
    )


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(main.app)


def create_test_client(get_db_function) -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    main.app.dependency_overrides[get_db_function] = get_test_db

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def agenda_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(agenda.get_db)


@pytest.fixture(scope="session")
def notification_test_client():
    yield from create_test_client(notification.get_db)


@pytest.fixture(scope="session")
def friendview_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(friendview.get_db)


@pytest.fixture(scope="session")
def weight_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(weight.get_db)


@pytest.fixture(scope="session")
def event_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(event.get_db)


@pytest.fixture(scope="session")
def home_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(main.get_db)


@pytest.fixture(scope="session")
def categories_test_client() -> Generator[TestClient, None, None]:
    yield from create_test_client(categories.get_db)


@pytest.fixture(scope="session")
def profile_test_client() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    main.app.dependency_overrides[profile.get_db] = get_test_db
    main.app.dependency_overrides[
        profile.get_placeholder_user
    ] = get_test_placeholder_user

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def quotes_test_client() -> Iterator[TestClient]:
    yield from create_test_client(main.get_db)


@pytest.fixture(scope="session")
def audio_test_client() -> Iterator[TestClient]:
    yield from create_test_client(audio.get_db)


@pytest.fixture(scope="session")
def security_test_client():
    yield from create_test_client(event.get_db)


@pytest.fixture(scope="session")
def salary_test_client() -> Iterator[TestClient]:
    yield from create_test_client(salary.get_db)


@pytest.fixture(scope="session")
def meds_test_client() -> Iterator[TestClient]:
    yield from create_test_client(meds.get_db)


@pytest.fixture(scope="session")
def google_connect_test_client():
    Base.metadata.create_all(bind=test_engine)
    main.app.dependency_overrides[google_connect.get_db] = get_test_db

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def dayview_test_client() -> Iterator[TestClient]:
    yield from create_test_client(dayview.get_db)


@pytest.fixture(scope="session")
def weekview_test_client() -> Iterator[TestClient]:
    yield from create_test_client(weekview.get_db)
