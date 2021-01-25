import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.database import engine

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.invitation_fixture',
    'tests.association_fixture',
    'tests.client_fixture',
    'tests.category_fixture',
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
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=test_engine)
