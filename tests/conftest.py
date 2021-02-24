import calendar

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PSQL_ENVIRONMENT
from app.database.models import Base

pytest_plugins = [
    "fixtures.tests.user_fixture",
    "fixtures.tests.event_fixture",
    "fixtures.tests.dayview_fixture",
    "fixtures.tests.invitation_fixture",
    "fixtures.tests.association_fixture",
    "fixtures.tests.client_fixture",
    "fixtures.tests.weekly_tasks_fixture",
    "fixtures.tests.asyncio_fixture",
    "fixtures.tests.logger_fixture",
    "fixtures.tests.category_fixture",
    "fixtures.tests.quotes_fixture",
    "fixtures.tests.zodiac_fixture",
    "fixtures.tests.jokes_fixture",
    "fixtures.tests.comment_fixture",
    "smtpdfix",
]

# When testing in a PostgreSQL environment please make sure that:
#   - Base string is a PSQL string
#   - app.config.PSQL_ENVIRONMENT is set to True

if PSQL_ENVIRONMENT:
    SQLALCHEMY_TEST_DATABASE_URL = (
        "postgresql://postgres:1234" "@localhost/postgres"
    )
    test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

else:
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
    test_engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


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


@pytest.fixture
def sqlite_engine():
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
    sqlite_test_engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    TestingSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sqlite_test_engine,
    )

    yield sqlite_test_engine
    session = TestingSession()
    session.close()
    Base.metadata.drop_all(bind=sqlite_test_engine)


@pytest.fixture
def Calendar():
    return calendar.Calendar(0)
