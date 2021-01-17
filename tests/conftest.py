from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base
from app.database.models import User
from app.routers import profile


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    return TestingSessionLocal()


def get_test_user():
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture
def profile_test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[profile.get_db] = get_test_db
    app.dependency_overrides[profile.get_new_user] = get_test_user

    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}
