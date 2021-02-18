from datetime import datetime, timedelta

from httpx import AsyncClient
import pytest

from app.database.models import Base
from app.main import app
from app.routers import telegram
from app.routers.event import create_event
from tests.client_fixture import get_test_placeholder_user
from tests.conftest import get_test_db, test_engine


@pytest.fixture
async def telegram_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[telegram.get_db] = get_test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)


today_date = datetime.today().replace(hour=0, minute=0, second=0)


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
        is_google_event=False,
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
        is_google_event=False,
    )
    yield user
    Base.metadata.drop_all(bind=test_engine)
