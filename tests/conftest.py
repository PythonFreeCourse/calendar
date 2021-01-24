import pytest
from datetime import datetime, timedelta

date_test_data = [(datetime.today() - timedelta(1), datetime.today())]

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def event_test_data():
    a = {'title': "Test Title",
        "location": "Fake City",
        "start_date": datetime.today() - timedelta(1),
        "end_date": datetime.today(),
        "vc_link": "https://fakevclink.com",
        "content": "Any Words",
        "owner_id": 123
        }
    return a 


@pytest.fixture
def date_test_data():
    return [datetime.today() - timedelta(1),
            datetime.today()
            ]
