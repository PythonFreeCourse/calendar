import pytest
from app.database.models import Event, User
from app.routers import profile
from fastapi import status
import os

class TestHolidaysImport:
    HOLIDAYS = '/profile/import_holidays'

    @staticmethod
    def create_user(session):
        user = User(username='testuser', email='test@abc.com', password='1234')
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def test_import_holidays_page_exists(client):
        resp = client.get(TestHolidaysImport.HOLIDAYS)
        assert resp.status_code == status.HTTP_200_OK
        assert b'Import holidays using ics file' in resp.content

    @pytest.mark.asyncio
    async def test_get_holidays(self, session):
        TestHolidaysImport.create_user(session)
        cwd = os.getcwd()
        with open(f'{cwd}/ics_example.txt', 'r') as file:
            ics_content = file.read()
            holidays = profile.get_holidays_from_file(ics_content, session)
            await profile.save_holidays_to_db(holidays, session)
        assert len(session.query(Event).all()) == 4
