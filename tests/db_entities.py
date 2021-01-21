import datetime

import pytest
from faker import Faker

from app.database.models import User, Event, Category


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


@pytest.fixture
def category(session, user):
    category = Category.create(session, name="Guitar Lesson", color="121212", user_id=user.id)
    yield category
    session.delete(category)
    session.commit()
