import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.invitation_fixture',
    'tests.association_fixture',
    'tests.client_fixture',
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
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session():
    Base.metadata.create_all(bind=test_engine)
    test_session = TestingSessionLocal()
    yield test_session
    test_session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def user(session):
    faker = Faker()
    user1 = User(username=faker.first_name(), email=faker.email())
    session.add(user1)
    session.commit()
    yield user1
    session.delete(user1)
    session.commit()


@pytest.fixture
def event(session, user):
    event1 = Event(
        title="Test Email", content="Test TEXT",
        start=datetime.datetime.now(),
        end=datetime.datetime.now(), owner_id=user.id)
    session.add(event1)
    session.commit()
    yield event1
    session.delete(event1)
    session.commit()


def get_test_placeholder_user():
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName'
    )


@pytest.fixture
def profile_test_client():
    Base.metadata.drop_all(bind=test_engine)
