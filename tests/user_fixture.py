from typing import Generator

import pytest
from app.database.models import User, UserExercise
from app.internal.utils import create_model, delete_instance
from datetime import datetime
from sqlalchemy.orm import Session


@pytest.fixture
def user(session: Session) -> Generator[User, None, None]:
    mock_user = create_model(
        session,
        User,
        username="test_username",
        password="test_password",
        email="test.email@gmail.com",
        language_id=1,
    )
    yield mock_user
    delete_instance(session, mock_user)


@pytest.fixture
def user_exercise(session: Session, user: User) -> UserExercise:
    test_user_exercise = create_model(
        session, UserExercise,
        user_id=11,
        start_date=datetime.now()
    )
    yield test_user_exercise
    delete_instance(session, test_user_exercise)


@pytest.fixture
def sender(session: Session) -> Generator[User, None, None]:
    mock_user = create_model(
        session,
        User,
        username="sender_username",
        password="sender_password",
        email="sender.email@gmail.com",
        language_id=1,
    )
    yield mock_user
    delete_instance(session, mock_user)
