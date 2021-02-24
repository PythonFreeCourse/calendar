import pytest
from sqlalchemy.orm import Session

from app.database.models import Quote
from app.internal.utils import create_model, delete_instance


def add_quote(
        session: Session, id_quote: int, text: str, author: str
) -> Quote:
    quote = create_model(
        session,
        Quote,
        id=id_quote,
        text=text,
        author=author,
    )
    yield quote
    delete_instance(session, quote)


@pytest.fixture
def quote1(session: Session) -> Quote:
    yield from add_quote(
        session=session,
        id_quote=1,
        text='You have to believe in yourself.',
        author='Sun Tzu',
    )


@pytest.fixture
def quote2(session: Session) -> Quote:
    yield from add_quote(
        session=session,
        id_quote=2,
        text='Wisdom begins in wonder.',
        author='Socrates',
    )
