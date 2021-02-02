import datetime

import pytest
import requests
from app.internal.celebrity import (get_celebs, get_content,
                                    get_today_month_and_day)
from fastapi import status


CELEBRITY_PAGE = "/celebrity"
FAKE_TIME = datetime.date(2018, 9, 18)
URL = 'tests/utils/mocking_celebrity_page.html'  # 01-28 birthdays

try:
    with open(URL, 'rb') as f:
        CONTENT = f.read()
except FileNotFoundError:
    URL = 'https://www.imdb.com/search/name/?birth_monthday=01-28'
    CONTENT = requests.get(URL).content


@pytest.fixture
def datetime_mock(monkeypatch):
    class MyDateTime:
        @classmethod
        def today(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'date', MyDateTime)


@pytest.fixture
def requests_mock(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.url = 'tests/utils/mocking_celebrity_page.html'
            self.content = CONTENT

    def mock_requests_get(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get)


@pytest.fixture
def requests_none_mock(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 403
            self.url = ''
            self.content = None

    def mock_requests_none(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_none)


@pytest.fixture
def requests_error_mock(monkeypatch):
    class MockResponse:
        def __init__(self):
            raise requests.ConnectionError("Test")

    def mock_requests_error(url):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_error)


def test_get_today_month_and_day(datetime_mock):
    assert get_today_month_and_day() == FAKE_TIME.strftime("%m-%d")


def test_celebrity_page_exists(client, requests_mock):
    resp = client.get(CELEBRITY_PAGE)
    assert resp.status_code == status.HTTP_200_OK
    assert b'born today' in resp.content


def test_internal_functions(requests_mock):
    # The date doesn't matter because of the patching
    celeb_dict = get_celebs('01-29')
    assert 'Ariel Winter' in celeb_dict  # Birthday - 01-28
    assert 'Tom Selleck' not in celeb_dict  # Birthday - 01-29


def test_no_response(requests_none_mock):
    assert get_content('') is None
    assert get_celebs('') is None


def test_error_response(requests_error_mock):
    assert get_content('') is None
