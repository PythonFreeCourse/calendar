from sqlalchemy.orm import Session

from app.dependencies import get_db


class TestApp:

    @staticmethod
    def test_get_db():
        assert isinstance(next(get_db()), Session)
