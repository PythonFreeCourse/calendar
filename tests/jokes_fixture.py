import pytest
from sqlalchemy.orm import Session

from app.database.models import Joke
from app.internal.utils import create_model, delete_instance


def add_joke(session: Session, id_joke: int, text: str) -> Joke:
    joke = create_model(session, Joke, id=id_joke, text=text)
    yield joke
    delete_instance(session, joke)


@pytest.fixture
def joke(session: Session) -> Joke:
    yield from add_joke(
        session=session,
        id_joke=1,
        text='Chuck Norris can slam a revolving door.',
    )
