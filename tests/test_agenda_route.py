from datetime import date, datetime, timedelta

from fastapi import status

from app.database.models import User, Event


class TestAgenda:
    AGENDA = "/agenda"
    AGENDA_7_DAYS = "/agenda?days=7"
    AGENDA_30_DAYS = "/agenda?days=30"
    NO_EVENTS = b"No events found..."
    INVALID_DATES = b"Start date is greater than end date"

    @staticmethod
    def base_today_date():
        return datetime.today().replace(hour=0, minute=0, second=0)

    @staticmethod
    def create_user_1(session):
        user = User(username='zohar', email='aa.aa@aa.com', password='1234')
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def create_user_2(session):
        user2 = User(username='dani', email='bb.aa@aa.com', password='12345')
        session.add(user2)
        session.commit()
        return user2

    @staticmethod
    def add_event(session, title, content, start, end, owner_id):
        event = Event(
            title=title, content=content,
            start=start, end=end, owner_id=owner_id
            )
        session.add(event)
        session.commit()

    @staticmethod
    def create_data_user_1(session):
        user = TestAgenda.create_user_1(session)
        base_date = TestAgenda.base_today_date()
        # Today event
        TestAgenda.add_event(
            session, "event 1", "...",
            base_date + timedelta(hours=7),
            base_date + timedelta(hours=9), user.id
            )
        # Today event
        TestAgenda.add_event(
            session, "event 2", "...",
            base_date + timedelta(hours=3),
            base_date + timedelta(days=2, hours=3), user.id
            )
        # Yesterday event
        TestAgenda.add_event(
            session, "event 3", "..",
            base_date - timedelta(hours=8),
            base_date, user.id
            )
        # Event in this week
        TestAgenda.add_event(
            session, "event 4", "...",
            base_date + timedelta(days=7, hours=2),
            base_date + timedelta(days=7, hours=4), user.id
            )
        # Event in this month.
        TestAgenda.add_event(
            session, "event 5", "...",
            base_date + timedelta(days=20, hours=4),
            base_date + timedelta(days=20, hours=6), user.id
            )
        # Old event
        TestAgenda.add_event(
            session, "event 6", "..",
            base_date - timedelta(days=5),
            base_date, user.id
            )

    @staticmethod
    def create_data_user_2(session):
        user2 = TestAgenda.create_user_2(session)
        base_date = TestAgenda.base_today_date()
        TestAgenda.add_event(
            session, "event 7", "..", base_date + timedelta(hours=7),
            base_date + timedelta(hours=8), user2.id
            )

    @staticmethod
    def test_agenda_page_no_arguments_when_no_today_events(client):
        resp = client.get(TestAgenda.AGENDA)
        assert resp.status_code == status.HTTP_200_OK
        assert TestAgenda.NO_EVENTS in resp.content

    @staticmethod
    def test_agenda_page_no_arguments_when_today_events_exist(client, session):
        TestAgenda.create_data_user_1(session)
        resp = client.get(TestAgenda.AGENDA)
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 1" in resp.content
        assert b"event 2" in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" not in resp.content
        assert b"event 5" not in resp.content
        assert b"event 6" not in resp.content

    @staticmethod
    def test_agenda_per_7_days(client, session):
        TestAgenda.create_data_user_1(session)
        resp = client.get(TestAgenda.AGENDA_7_DAYS)
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
    def test_agenda_per_30_days(client, session):
        TestAgenda.create_data_user_1(session)
        resp = client.get(TestAgenda.AGENDA_30_DAYS)
        today = date.today().strftime("%d/%m/%Y")
        assert resp.status_code == status.HTTP_200_OK
        assert bytes(today, 'utf-8') in resp.content
        assert b"event 1" in resp.content
        assert b"event 2" in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" in resp.content
        assert b"event 5" in resp.content
        assert b"event 6" not in resp.content

    @staticmethod
    def test_agenda_between_two_dates(client, session):
        TestAgenda.create_data_user_1(session)
        base_date = TestAgenda.base_today_date()
        start_date = (base_date + timedelta(days=8, hours=4)).date()
        end_date = (base_date + timedelta(days=32, hours=4)).date()
        resp = client.get(
            f"/agenda?start_date={start_date}&end_date={end_date}")
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 1" not in resp.content
        assert b"event 2" not in resp.content
        assert b"event 3" not in resp.content
        assert b"event 4" not in resp.content
        assert b"event 5" in resp.content
        assert b"event 6" not in resp.content

    @staticmethod
    def test_agenda_start_bigger_than_end(client):
        base_date = TestAgenda.base_today_date()
        start_date = base_date.date()
        end_date = (base_date - timedelta(days=2)).date()
        resp = client.get(
            f"/agenda?start_date={start_date}&end_date={end_date}")
        assert resp.status_code == status.HTTP_200_OK
        assert TestAgenda.INVALID_DATES in resp.content

    @staticmethod
    def test_no_show_events_user_2(client, session):
        TestAgenda.create_data_user_1(session)
        TestAgenda.create_data_user_2(session)
        resp = client.get(TestAgenda.AGENDA)
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 7" not in resp.content
