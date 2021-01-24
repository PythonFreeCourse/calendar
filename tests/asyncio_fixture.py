from httpx import AsyncClient
import pytest

from app.database.database import Base
from app.main import app
from app.routers import telegram
from tests.conftest import test_engine, get_test_db


@pytest.fixture
async def telegram_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[telegram.get_db] = get_test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {}
    Base.metadata.drop_all(bind=test_engine)
