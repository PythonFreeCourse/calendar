import calendar

import pytest


@pytest.fixture
def Calendar():
    return calendar.Calendar(0)
