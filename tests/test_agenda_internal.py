from datetime import datetime

from app.internal import agenda_events
import pytest

START = datetime(2021, 11, 1, 8, 00, 00)

dates = [
    (START, datetime(2021, 11, 3, 8, 00, 0), '2 days'),
    (START, datetime(2021, 11, 3, 10, 30, 0), '2 days 2 hours and 30 minutes'),
    (START, datetime(2021, 11, 1, 8, 30, 0), '30 minutes'),
    (START, datetime(2021, 11, 1, 10, 00, 0), '2 hours'),
    (START, datetime(2021, 11, 1, 10, 30, 0), '2 hours and 30 minutes'),
    (START, datetime(2021, 11, 2, 10, 00, 0), 'a day and 2 hours'),
]


@pytest.mark.parametrize('start, end, diff', dates)
def test_get_time_delta_string(start, end, diff):
    assert agenda_events.get_time_delta_string(start, end) == diff
