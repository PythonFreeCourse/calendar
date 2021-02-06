from sqlalchemy.orm import Session


from app.database.database import get_db


class TestApp:

    @staticmethod
    def test_get_db():
        assert isinstance(next(get_db()), Session)

    @staticmethod
    def test_session_db():
        assert get_db() is not None
