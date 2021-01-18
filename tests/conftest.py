import pytest
from app.database.database import Base, SessionLocal, engine
from app.main import app
from fastapi.testclient import TestClient

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.invitation_fixture'
]


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
