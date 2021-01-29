from datetime import datetime, timedelta


from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


from app.main import app
from app.routers.event import add_new_event, check_date_validation
from app.database.database import get_db


class TestApp:

    client = TestClient(app)
    date_test_data = [datetime.today() - timedelta(1), datetime.today()]
    event_test_data = {
            'title': "Test Title",
            "location": "Fake City",
            "start": date_test_data[0],
            "end": date_test_data[1],
            "vc_link": "https://fakevclink.com",
            "content": "Any Words",
            "owner_id": 123}

    @staticmethod
    def test_get_db():
        assert isinstance(next(get_db()), Session)

    @staticmethod
    def test_session_db():
        assert get_db() is not None

    @staticmethod
    def check_date_validation():
        start = TestApp.date_test_data[0]
        end = TestApp.date_test_data[1]
        assert check_date_validation(start, end)

    @staticmethod
    def test_bad_check_validation():
        assert not check_date_validation(
            TestApp.date_test_data[0],
            'd'
                                )

    @staticmethod
    def test_add_event(session: Session):
        assert add_new_event(TestApp.event_test_data, session) is not None

    @staticmethod
    def test_add_bad_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data['no_colume'] = 'some data'
        assert add_new_event(bad_event_test_data, session) is None

    @staticmethod
    def test_add_bad_times_to_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data['start'] = TestApp.date_test_data[1]
        bad_event_test_data['end'] = TestApp.date_test_data[0]
        assert add_new_event(bad_event_test_data, session) is None
