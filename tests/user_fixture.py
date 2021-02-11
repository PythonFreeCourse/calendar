import pytest
from sqlalchemy.orm import Session

from app.database.models import User
from app.internal.utils import create_model, delete_instance


@pytest.fixture
def user(session: Session) -> User:
    test_user = create_model(
        session, User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
        language='english',
        language_id=1
    )
    yield test_user
    delete_instance(session, test_user)


@pytest.fixture
def sender(session: Session) -> User:
    sender = create_model(
        session, User,
        username='sender_username',
        password='sender_password',
        email='sender.email@gmail.com',
        language='english',
        language_id=1
    )
    yield sender
    delete_instance(session, sender)
