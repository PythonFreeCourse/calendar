import pytest

from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    client = TestClient(app)
    return client