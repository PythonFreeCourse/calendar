import pytest
from sqlalchemy.orm import Session

from app.database.models import Zodiac
from tests.utils import create_model, delete_instance


@pytest.fixture
def zodiac1(session: Session) -> Zodiac:
    zodiac = create_model(
        session, Zodiac,
        name="aries",
        start_month=3,
        start_day_in_month=20,
        end_month=4,
        end_day_in_month=19,
    )
    yield zodiac
    delete_instance(session, zodiac)
