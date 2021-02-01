import datetime
import pytest
import requests
import responses

from app.internal.astronomy import get_astronomical_data
from app.internal.astronomy import ASTRONOMY_URL

RESPONSE_FROM_MOCK = {"location": {
        "name": "Tel Aviv-Yafo",
        "region": "Tel Aviv",
        "country": "Israel",
        "lat": 32.07,
        "lon": 34.76,
        "tz_id": "Asia/Jerusalem",
        "localtime_epoch": 1611399607,
        "localtime": "2021-01-23 13:00"
    },
    "astronomy": {
        "astro": {
            "sunrise": "05:25 AM",
            "sunset": "06:03 PM",
            "moonrise": "01:56 PM",
            "moonset": "03:04 AM",
            "moon_phase": "Waxing Gibbous",
            "moon_illumination": "79"
        }
    }
}
ERROR_RESPONSE_FROM_MOCK = {"error": {"message": "Error Text"}}


@pytest.mark.asyncio
def test_get_astronomical_data(httpx_mock):
    requested_date = datetime.datetime(day=4, month=4, year=2020)
    httpx_mock.add_response(method="GET", json=RESPONSE_FROM_MOCK)
    output = get_astronomical_data(requested_date, "tel aviv")
    assert output['Success']


def test_astronomical_data_error_from_api(requests_mock):
    requested_date = datetime.datetime(day=4, month=4, year=2021)
    requests_mock.get(ASTRONOMY_URL, json=ERROR_RESPONSE_FROM_MOCK)
    output = get_astronomical_data(requested_date, "123")
    assert not output['Success']


@responses.activate
def test_astronomical_exception_from_api():
    requested_date = datetime.datetime.now() + datetime.timedelta(days=3)
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(ASTRONOMY_URL)
    output = get_astronomical_data(requested_date, "456")
    assert not output['Success']


@responses.activate
def test_astronomical_no_response_from_api():
    requested_date = datetime.datetime(day=11, month=1, year=2020)
    responses.add(responses.GET, ASTRONOMY_URL, status=500)
    requests.get(ASTRONOMY_URL)
    output = get_astronomical_data(requested_date, "789")
    assert not output['Success']
