from sqlalchemy.orm import Session

import pytest

from app.database.database import get_db


class TestApp:

    @pytest.mark.app
    def test_get_db(self):
        assert isinstance(next(get_db()), Session)

    @staticmethod
    @pytest.mark.app
    def test_home(client):
        response = client.get("/")
        assert response.ok
