from datetime import date, time

import pytest
from sqlalchemy.orm import Session

from app.database.models import User
from app.internal import utils


TIMES = [
    ('2021-01-14', date(2021, 1, 14)),
    ('13:30', time(13, 30)),
    ('15:42:00', time(15, 42)),
    ('15', None),
    ('2021-01', None),
    ('15:42:00.5', None),
]


class TestUtils:

    def test_save_success(self, user: User, session: Session) -> None:
        user.username = 'edit_username'
        assert utils.save(session, user)

    def test_save_failure(self, session: Session) -> None:
        user = 'not a user instance'
        assert not utils.save(session, user)

    def test_create_model(self, session: Session) -> None:
        assert session.query(User).first() is None
        info = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test1234'
        }
        utils.create_model(session, User, **info)
        assert session.query(User).first()

    def test_delete_instance(self, session: Session, user: User):
        assert session.query(User).first()
        utils.delete_instance(session, user)
        assert session.query(User).first() is None

    def test_get_current_user(self, session: Session) -> None:
        # Code revision required after user login feature is added
        assert session.query(User).filter_by(id=1).first() is None
        utils.get_current_user(session)
        assert session.query(User).filter_by(id=1).first()

    def test_get_user(self, user: User, session: Session) -> None:
        assert utils.get_user(session, user.id) == user
        assert utils.get_user(session, 2) is None

    @pytest.mark.parametrize('string, formatted_time', TIMES)
    def test_get_time_from_string(self, string: str,
                                  formatted_time: time) -> None:
        assert utils.get_time_from_string(string) == formatted_time
