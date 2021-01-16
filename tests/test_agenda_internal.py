from datetime import datetime

from app.internal import agenda_events
import pytest

start = datetime(2021, 11, 1, 8, 00, 00)
end1 = datetime(2021, 11, 3, 8, 00, 00)
end2 = datetime(2021, 11, 3, 10, 30, 00)
end3 = datetime(2021, 11, 1, 8, 30, 00)
end4 = datetime(2021, 11, 1, 10, 00, 00)
end5 = datetime(2021, 11, 1, 10, 30, 00)
end6 = datetime(2021, 11, 2, 10, 00, 00)
diff1 = '2 days'
diff2 = '2 days, 2:30 hours'
diff3 = '30 minutes'
diff4 = '2 hours'
diff5 = '2:30 hours'
diff6 = '1 days, 2 hours'

dates = [
    (start, end1, diff1),
    (start, end2, diff2),
    (start, end3, diff3),
    (start, end4, diff4),
    (start, end5, diff5),
    (start, end6, diff6),
]


@pytest.mark.parametrize('start, end, diff', dates)
def test_get_time_delta_string(start, end, diff):
    assert agenda_events.get_time_delta_string(start, end) == diff

