from collections import Generator

import pytest
from sqlalchemy.orm import Session

from app.database.models import User
from app.internal.utils import create_model, delete_instance


@pytest.fixture
def user(session: Session) -> Generator[User, None, None]:
    mock_user = create_model(
        session, User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
        language_id=1,
    )
    yield mock_user
    delete_instance(session, mock_user)


@pytest.fixture
def sender(session: Session) -> Generator[User, None, None]:
    mock_user = create_model(
        session, User,
        username='sender_username',
        password='sender_password',
        email='sender.email@gmail.com',
        language_id=1,
    )
    yield mock_user
    delete_instance(session, mock_user)
