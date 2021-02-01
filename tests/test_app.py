from sqlalchemy.orm import Session

from app.database.database import get_db


class TestApp:

    def test_get_db(self):
        assert isinstance(next(get_db()), Session)

    def test_home(client):
        response = client.get("/")
        assert response.ok
