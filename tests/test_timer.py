from datetime import datetime
from app.internal import timer
import pytest

from app.internal.timer import get_next_user_event, get_next_user_event_start_time


def test_get_last_event_success(event, session):
    next_event = get_next_user_event(
        session=session,
        user_id=event.owner_id,
    )
    assert next_event == event


def test_time_left(event, session):
    time_left = get_next_user_event_start_time(
        session=session,
        user_id=event.owner_id,
    )
    assert type(time_left["timer"]) is str
