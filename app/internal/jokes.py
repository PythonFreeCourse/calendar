from app.database.models import Joke

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func


def get_a_joke(session: Session):
    joke = session.query(Joke).order_by(func.random()).first()
    return joke