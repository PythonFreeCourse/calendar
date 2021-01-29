import pytest
from sqlalchemy.orm import Session

from app.database.models import User
from tests.utils import create_model, delete_instance


@pytest.fixture
def user(session: Session) -> User:
    test_user = create_model(
        session, User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
    )
    yield test_user
    delete_instance(session, test_user)


@pytest.fixture
def user2(session: Session) -> User:
    test_user2 = create_model(
        session, User,
        username='test_username2',
        password='test_password2',
        email='test2.email@gmail.com',
    )
    yield test_user2
    delete_instance(session, test_user2)


@pytest.fixture
def sender(session: Session) -> User:
    sender = create_model(
        session, User,
        username='sender_username',
        password='sender_password',
        email='sender.email@gmail.com',
    )
    yield sender
    delete_instance(session, sender)
