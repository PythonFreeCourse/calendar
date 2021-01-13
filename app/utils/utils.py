from app.config import session


def save(item) -> None:
    session.add(item)
    session.commit()
