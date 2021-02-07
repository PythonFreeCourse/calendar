import pytest
from sqlalchemy.orm import Session

from app.database.models import User, Category


@pytest.fixture
def category(session: Session, sender: User) -> Category:
    category = Category.create(session, name="Guitar Lesson", color="121212",
                               user_id=sender.id)
    yield category
    session.delete(category)
    session.commit()
