from datetime import date, datetime, timedelta

from fastapi import status


class TestAgenda:
    """In the test we are receiving event fixtures
    as parameters so they will load into the database"""

    AGENDA = "/agenda"
    AGENDA_7_DAYS = "/agenda?days=7"
    AGENDA_30_DAYS = "/agenda?days=30"
    NO_EVENTS = b"No events found..."
    INVALID_DATES = b"Start date is greater than end date"
    today_date = datetime.today().replace(hour=0, minute=0, second=0)

    @staticmethod
    def test_agenda_page_no_arguments_when_no_today_events(
            agenda_test_client, session):
        resp = agenda_test_client.get(TestAgenda.AGENDA)
        assert resp.status_code == status.HTTP_200_OK
        assert TestAgenda.NO_EVENTS in resp.content

    def test_agenda_page_no_arguments_when_today_events_exist(
            self, agenda_test_client, session, sender, today_event,
            today_event_2, yesterday_event, next_week_event,
            next_month_event, old_event
    ):
        resp = agenda_test_client.get(TestAgenda.AGENDA)
        assert resp.ok
        assert b"event 1" in resp.content
        assert b"event 2" in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" not in resp.content
        assert b"event 5" not in resp.content
        assert b"event 6" not in resp.content

    @staticmethod
    def test_agenda_per_7_days(
            agenda_test_client, session, sender, today_event,
            today_event_2, yesterday_event, next_week_event,
            next_month_event, old_event
    ):
        resp = agenda_test_client.get(TestAgenda.AGENDA_7_DAYS)
        today = date.today().strftime("%d/%m/%Y")
        assert resp.status_code == status.HTTP_200_OK
        assert bytes(today, 'utf-8') in resp.content
        assert b"event 1" in resp.content
        assert b"event 2" in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" in resp.content
        assert b"event 5" not in resp.content
        assert b"event 6" not in resp.content

    @staticmethod
    def test_agenda_per_30_days(
            agenda_test_client, session, sender, today_event,
            today_event_2, yesterday_event, next_week_event,
            next_month_event, old_event
    ):
        resp = agenda_test_client.get(TestAgenda.AGENDA_30_DAYS)
        today = date.today().strftime("%d/%m/%Y")
        assert resp.status_code == status.HTTP_200_OK
        assert bytes(today, 'utf-8') in resp.content
        assert b"event 1" in resp.content
        assert b"event 2" in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" in resp.content
        assert b"event 5" in resp.content
        assert b"event 6" not in resp.content

    def test_agenda_between_two_dates(
            self, agenda_test_client, session, sender, today_event,
            today_event_2, yesterday_event, next_week_event,
            next_month_event, old_event
    ):
        start_date = (self.today_date + timedelta(days=8, hours=4)).date()
        end_date = (self.today_date + timedelta(days=32, hours=4)).date()
        resp = agenda_test_client.get(
            f"/agenda?start_date={start_date}&end_date={end_date}")
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 1" not in resp.content
        assert b"event 2" not in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" not in resp.content
        assert b"event 5" in resp.content
        assert b"event 6" not in resp.content

    def test_agenda_start_bigger_than_end(self, agenda_test_client):
        start_date = self.today_date.date()
        end_date = (self.today_date - timedelta(days=2)).date()
        resp = agenda_test_client.get(
            f"/agenda?start_date={start_date}&end_date={end_date}")
        assert resp.status_code == status.HTTP_200_OK
        assert TestAgenda.INVALID_DATES in resp.content

    @staticmethod
    def test_no_show_events_user_2(
            agenda_test_client, session, sender, today_event,
            today_event_2, yesterday_event, next_week_event,
            next_month_event, old_event
    ):
        # "user" is just a different event creator
        resp = agenda_test_client.get(TestAgenda.AGENDA)
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 7" not in resp.content
