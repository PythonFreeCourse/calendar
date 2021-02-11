from datetime import datetime, timedelta

from httpx import AsyncClient
import pytest

from app.database.database import Base
from app.database.models import User
from app.main import app
from app.routers import telegram
from app.routers.event import create_event
from tests.conftest import test_engine, get_test_db


@pytest.fixture
async def telegram_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[telegram.get_db] = get_test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


today_date = datetime.today().replace(hour=0, minute=0, second=0)


def get_test_placeholder_user():
    return User(
        username='fake_user',
        email='fake@mail.fake',
        password='123456fake',
        full_name='FakeName',
        language_id=1,
        telegram_id='666666'
    )


@pytest.fixture
def fake_user_events(session):
    Base.metadata.create_all(bind=test_engine)
    user = get_test_placeholder_user()
    session.add(user)
    session.commit()
    create_event(
        db=session,
        title='Cool today event',
        start=today_date,
        end=today_date + timedelta(days=2),
        all_day=False,
        content='test event',
        owner_id=user.id,
        location="Here",
    )
    create_event(
        db=session,
        title='Cool (somewhen in two days) event',
        start=today_date + timedelta(days=1),
        end=today_date + timedelta(days=3),
        all_day=False,
        content='this week test event',
        owner_id=user.id,
        location="Here",
    )
    yield user
    Base.metadata.drop_all(bind=test_engine)
