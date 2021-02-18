from app.internal.showevent import get_upcoming_events


class TestShowview:

    def test_get_events_success(self, next_week_event, session):
        events = get_upcoming_events(
            session=session,
            user_id=next_week_event.owner_id,
        )
        assert list(events) == [next_week_event]

    def test_only_events_from_now_on(self, yesterday_event, session):
        events = get_upcoming_events(
            session=session,
            user_id=yesterday_event.owner_id,
        )
        assert list(events) == []
