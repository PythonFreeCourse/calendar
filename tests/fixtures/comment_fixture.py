from datetime import datetime
from typing import Iterator

import pytest
from sqlalchemy.orm.session import Session

from app.database.models import Comment, Event, User
from app.internal.utils import create_model, delete_instance


@pytest.fixture
def comment(session: Session, event: Event, user: User) -> Iterator[Comment]:
    data = {
        'user': user,
        'event': event,
        'content': 'test comment',
        'time': datetime(2021, 1, 1, 0, 1),
    }
    create_model(session, Comment, **data)
    comment = session.query(Comment).first()
    yield comment
    delete_instance(session, comment)
