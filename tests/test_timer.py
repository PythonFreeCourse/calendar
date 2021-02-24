from app.internal.timer import get_next_user_event
from app.internal.timer import get_next_user_event_start_time


def test_get_last_event_success(next_week_event, session):
    next_event = get_next_user_event(
        session=session,
        user_id=next_week_event.owner_id,
    )
    assert next_event == next_week_event


def test_time_left(next_week_event, session):
    time_left = get_next_user_event_start_time(
        session=session,
        user_id=next_week_event.owner_id,
    )
    assert isinstance(time_left["timer"], str)
