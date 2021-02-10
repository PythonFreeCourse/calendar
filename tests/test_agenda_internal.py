from datetime import date

from app.internal.agenda_events import get_events_per_dates


class TestAgenda:
    def test_get_events_per_dates_success(self, today_event, session):
        events = get_events_per_dates(
            session=session,
            user_id=today_event.owner_id,
            start=today_event.start.date(),
            end=today_event.end.date(),
        )
        assert list(events) == [today_event]

    def test_get_events_per_dates_failure(self, yesterday_event, session):
        events = get_events_per_dates(
            session=session,
            user_id=yesterday_event.owner_id,
            start=date.today(),
            end=date.today(),
        )
        assert list(events) == []
