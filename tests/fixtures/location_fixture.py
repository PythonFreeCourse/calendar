import pytest
from sqlalchemy.orm import Session

from app.database.models import Location
from app.internal.utils import create_model, delete_instance


def add_location(
        session: Session,
        id_location: int,
        country: str,
        city: str,
        zip_number: str,
) -> Location:
    location = create_model(
        session,
        Location,
        id=id_location,
        country=country,
        city=city,
        zip_number=zip_number)
    yield location
    delete_instance(session, location)


@pytest.fixture
def location(session: Session) -> Location:
    yield from add_location(
        session=session,
        id_location=1,
        country="AD",
        city="Andorra La Vella",
        zip_number="3041563"
    )
