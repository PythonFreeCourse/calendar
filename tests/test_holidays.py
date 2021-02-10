import os
from app.database.models import Event, User
from app.routers import profile
from sqlalchemy.orm import Session


class TestHolidaysImport:
    HOLIDAYS = '/profile/holidays/import'

    @staticmethod
    def test_import_holidays_page_exists(client):
        resp = client.get(TestHolidaysImport.HOLIDAYS)
        assert resp.ok
        assert b'Import holidays using ics file' in resp.content

    def test_get_holidays(self, session: Session, user: User):
        current_folder = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(current_folder, 'resources')
        test_file = os.path.join(resource_folder, 'ics_example.txt')
        with open(test_file) as file:
            ics_content = file.read()
            holidays = profile.get_holidays_from_file(ics_content, session)
            profile.save_holidays_to_db(holidays, session)
        assert len(session.query(Event).all()) == 4

    def test_wrong_file_get_holidays(self, session: Session, user: User):
        current_folder = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(current_folder, 'resources')
        test_file = os.path.join(resource_folder, 'wrong_ics_example.txt')
        with open(test_file) as file:
            ics_content = file.read()
            holidays = profile.get_holidays_from_file(ics_content, session)
            profile.save_holidays_to_db(holidays, session)
        assert len(session.query(Event).all()) == 0
