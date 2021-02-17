from datetime import timedelta

from icalendar import vCalAddress

from app.config import ICAL_VERSION, PRODUCT_ID
from app.internal import export
from app.internal.agenda_events import filter_dates
from app.routers.user import get_all_user_events


class TestExport:

    @staticmethod
    def test_export(client, sender, today_event):
        response = client.get('/export?start_date=&end_date=')
        assert isinstance(response.content, bytes)
        assert response.ok

    @staticmethod
    def test_get_events_no_time_frame(
            today_event, next_month_event, sender, session):
        start = None
        end = None
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert set(filtered_events) == {today_event, next_month_event}

    @staticmethod
    def test_get_events_end_time_frame_success(today_event, sender, session):
        start = None
        end = today_event.end.date()
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert list(filtered_events) == [today_event]

    @staticmethod
    def test_get_events_end_time_frame_failure(
            today_event, next_month_event, sender, session):
        start = None
        end = today_event.start.date() - timedelta(days=1)
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert list(filtered_events) == []

    @staticmethod
    def test_get_events_start_time_frame_success(
            today_event, next_month_event, sender, session):
        start = next_month_event.start.date()
        end = None
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert list(filtered_events) == [next_month_event]

    @staticmethod
    def test_get_events_start_time_frame_failure(
            today_event, next_month_event, sender, session):
        start = next_month_event.start.date() + timedelta(days=1)
        end = None
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert list(filtered_events) == []

    @staticmethod
    def test_get_events_start_and_end_time_frame_success(
            today_event, next_month_event, sender, session):
        start = today_event.start.date()
        end = next_month_event.start.date()
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert set(filtered_events) == {today_event, next_month_event}

    @staticmethod
    def test_get_events_start_and_end_time_frame_failure(
            today_event, next_month_event, sender, session):
        start = today_event.start.date() + timedelta(days=1)
        end = next_month_event.start.date() - timedelta(days=1)
        events = get_all_user_events(session, sender.id)
        filtered_events = filter_dates(events, start, end)
        assert list(filtered_events) == []

    class TestExportInternal:

        @staticmethod
        def test_create_icalendar():
            icalendar = export._create_icalendar()
            assert icalendar.get('version') == ICAL_VERSION
            assert icalendar.get('prodid') == PRODUCT_ID

        @staticmethod
        def test_create_icalendar_event(event):
            ievent = export._create_icalendar_event(event)
            assert event.owner.email in ievent.get('organizer')
            assert ievent.get('summary') == event.title

        @staticmethod
        def test_get_v_cal_address(event, user):
            email = "test_email"
            v_cal_address = export._get_v_cal_address(email)
            test_v_cal_address = vCalAddress(f'MAILTO:{email}')
            assert v_cal_address == test_v_cal_address

        @staticmethod
        def test_get_icalendar(user, event):
            icalendar = export.get_icalendar(event, [user.email])

            def does_contain(item: str) -> bool:
                """Returns True if calendar contains item."""
                return bytes(item, encoding='utf8') in bytes(icalendar)

            assert does_contain(ICAL_VERSION)
            assert does_contain(PRODUCT_ID)
            assert does_contain(event.owner.email)
            assert does_contain(event.title)

        @staticmethod
        def test_get_icalendar_with_multiple_events(
                session, user, event, today_event):
            icalendar = export.get_icalendar_with_multiple_events(
                session, [event, today_event])

            assert icalendar
