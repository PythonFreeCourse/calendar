import pytest
from datetime import datetime, timedelta

from app.database.database import get_db


# @pytest.fixture
# def db():
#     for i in get_db():
#         my_db = i
#     return my_db

# @pytest.fixture
# def event_test_data():
#     date_test_data = [(datetime.today() - timedelta(1), datetime.today())]
#     return [(
#         {'title': "Test Title",
#         "location": "Fake City",
#         "start_date": date_test_data[0][0],
#         "end_date": date_test_data[0][1],
#         "vc_link": "https://fakevclink.com",
#         "content": "Any Words",
#         "owner_id": 123},
#         db()
#     )]

# @pytest.fixture
# def date_test_data():
#     return [datetime.today() - timedelta(1),
#             datetime.today()
#             ]
