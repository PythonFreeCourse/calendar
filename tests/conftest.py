import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base

pytest_plugins = [
    'tests.user_fixture',
    'tests.event_fixture',
    'tests.invitation_fixture'
]


@pytest.fixture(scope="session")
def engine():
    return create_engine('sqlite:///', echo=False)


@pytest.fixture(scope="session")
def session(engine):
    session = sessionmaker(bind=engine)()
    Base.metadata.create_all(engine)
    yield session
    session.close()
