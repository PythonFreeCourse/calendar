import calendar
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PSQL_ENVIRONMENT
from app.database.models import Base
from app.routers.event import create_event
from app.routers.user import create_user

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.dayview_fixture',
    'tests.invitation_fixture',
    'tests.association_fixture',
    'tests.client_fixture',
    'tests.asyncio_fixture',
    'tests.logger_fixture',
    'tests.category_fixture',
    'smtpdfix',
    'tests.quotes_fixture',
    'tests.zodiac_fixture',
    'tests.comment_fixture',
]

# When testing in a PostgreSQL environment please make sure that:
#   - Base string is a PSQL string
#   - app.config.PSQL_ENVIRONMENT is set to True

if PSQL_ENVIRONMENT:
    SQLALCHEMY_TEST_DATABASE_URL = (
        "postgresql://postgres:1234"
        "@localhost/postgres"
    )
    test_engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL
    )

else:
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


@pytest.fixture
def sqlite_engine():
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
    sqlite_test_engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    TestingSession = sessionmaker(
        autocommit=False, autoflush=False, bind=sqlite_test_engine)

    yield sqlite_test_engine
    session = TestingSession()
    session.close()
    Base.metadata.drop_all(bind=sqlite_test_engine)


@pytest.fixture
def Calendar():
    return calendar.Calendar(0)


@pytest.fixture
def no_event_user(session):
    """a user made for testing who doesn't own any event."""
    user = create_user(
        session=session,
        username='new_test_username',
        password='new_test_password',
        email='new2_test.email@gmail.com',
        language_id='english'
    )

    return user


@pytest.fixture
def event_owning_user(session):
    """a user made for testing who already owns an event."""
    user = create_user(
        session=session,
        username='new_test_username2',
        password='new_test_password2',
        email='new_test_love231.email@gmail.com',
        language_id='english'
    )

    data = {
        'title': 'event_owning_user event',
        'start': datetime.strptime('2021-05-05 14:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-05-05 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/875384596',
        'content': 'content',
        'owner_id': user.id,
    }

    create_event(session, **data)

    return user


@pytest.fixture
def user1(session):
    """another user made for testing"""
    user = create_user(
        session=session,
        username='user2user2',
        password='verynicepass',
        email='trulyyours1.email@gmail.com',
        language_id='english'
    )
    return user


@pytest.fixture
def event_example(session, event_owning_user):
    data = {
        'title': 'test event title',
        'start': datetime.strptime('2021-05-05 14:59', '%Y-%m-%d %H:%M'),
        'end': datetime.strptime('2021-05-05 15:01', '%Y-%m-%d %H:%M'),
        'location': 'https://us02web.zoom.us/j/87538459r6',
        'content': 'content',
        'owner_id': event_owning_user.id,
    }

    event = create_event(session, **data)
    return event
