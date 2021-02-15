from datetime import timedelta

from icalendar import vCalAddress

from app.config import ICAL_VERSION, PRODUCT_ID
from app.internal.agenda_events import filter_dates
from app.internal.export import (
    create_ical_calendar, create_ical_event,
    event_to_ical
)
from app.routers.user import get_all_user_events


class TestExport:

    def test_export(self, client, sender, today_event):
        resp = client.get('/export?start_date=&end_date=')
        assert isinstance(resp.content, bytes)
        assert resp.ok

    def test_get_events_no_time_frame(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = None
        end = None
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert set(evens) == {today_event, next_month_event}

    def test_get_events_end_time_frame_success(
            self, today_event,
            sender, session
    ):
        start = None
        end = today_event.end.date()
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert list(evens) == [today_event]

    def test_get_events_end_time_frame_failure(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = None
        end = today_event.start.date() - timedelta(days=1)
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert list(evens) == []

    def test_get_events_start_time_frame_success(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = next_month_event.start.date()
        end = None
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert list(evens) == [next_month_event]

    def test_get_events_start_time_frame_failure(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = next_month_event.start.date() + timedelta(days=1)
        end = None
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert list(evens) == []

    def test_get_events_start_and_end_time_frame_success(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = today_event.start.date()
        end = next_month_event.start.date()
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert set(evens) == {today_event, next_month_event}

    def test_get_events_start_and_end_time_frame_failure(
            self, today_event,
            next_month_event,
            sender, session
    ):
        start = today_event.start.date() + timedelta(days=1)
        end = next_month_event.start.date() - timedelta(days=1)
        events = get_all_user_events(session, sender.id)
        evens = filter_dates(events, start, end)
        assert list(evens) == []

    def test_create_ical_calendar(self):
        cal = create_ical_calendar()
        assert cal.get('version') == ICAL_VERSION
        assert cal.get('prodid') == PRODUCT_ID

    def test_create_ical_event(self, event):
        ical_event = create_ical_event(event)
        assert event.owner.email in ical_event.get('organizer')
        assert ical_event.get('summary') == event.title

    def test_add_attendees(self, event, user):
        ical_event = create_ical_event(event)
        ical_event.add(
            'attendee',
            vCalAddress(f'MAILTO:{user.email}'),
            encode=0
        )
        attendee = vCalAddress(f'MAILTO:{user.email}')
        assert attendee == ical_event.get('attendee')

    def test_event_to_ical(self, user, event):
        ical_event = event_to_ical(event, [user.email])

        def does_contain(item: str) -> bool:
            """Returns if calendar contains item."""

            return bytes(item, encoding='utf8') in bytes(ical_event)

        assert does_contain(ICAL_VERSION)
        assert does_contain(PRODUCT_ID)
        assert does_contain(event.owner.email)
        assert does_contain(event.title)
