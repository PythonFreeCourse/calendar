from app.internal.showevent import get_upcoming_events


class TestShowview:

    def test_get_events_success(self, today_event, session):
        events = get_upcoming_events(
            session=session,
            user_id=today_event.owner_id,
        )
        assert list(events) == [today_event]

    def test_only_events_from_now_on(self, yesterday_event, session):
        events = get_upcoming_events(
            session=session,
            user_id=yesterday_event.owner_id,
        )
        assert list(events) == []
