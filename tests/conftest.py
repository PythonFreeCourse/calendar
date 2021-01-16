import datetime

import pytest
from app.database.database import Base, SessionLocal, engine
from app.database.models import Event, User
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sessions():
    Base.metadata.create_all(bind=engine)
    sessions = SessionLocal()
    User1 = User(username="Pure", email="ttxdxp@gmail.com")
    sessions.add(User1)
    sessions.commit()
    User2 = User(username="Idan_prog", email="pelled.idan@gmail.com")
    sessions.add(User2)
    sessions.commit()
    Event1 = Event(title="Welcome to Hell", content="JK this is a test email",
                   date=datetime.datetime.now(), owner_id=User1.id)
    sessions.add(Event1)
    sessions.commit()
    yield sessions
    Base.metadata.drop_all(bind=engine)
