import pytest
import requests


@pytest.fixture
def requests_mock_good(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200

    def mock_requests_get_good(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get_good)


@pytest.fixture
def requests_mock_bad(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 403

    def mock_requests_get_bad(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get_bad)


@pytest.fixture
def requests_mock_error(monkeypatch):
    class MockResponse:
        def __init__(self):
            raise requests.ConnectionError("Test")

    def mock_requests_error(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_error)
