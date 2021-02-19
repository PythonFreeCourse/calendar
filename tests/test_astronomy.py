import datetime

from fastapi import status
import httpx
import pytest
import requests
import responses
import respx

from app.internal.astronomy import ASTRONOMY_URL
from app.internal.astronomy import get_astronomical_data

RESPONSE_FROM_MOCK = {
    "location": {
        "name": "Tel Aviv-Yafo",
        "region": "Tel Aviv",
        "country": "Israel",
        "lat": 32.07,
        "lon": 34.76,
        "tz_id": "Asia/Jerusalem",
        "localtime_epoch": 1611399607,
        "localtime": "2021-01-23 13:00",
    },
    "astronomy": {
        "astro": {
            "sunrise": "05:25 AM",
            "sunset": "06:03 PM",
            "moonrise": "01:56 PM",
            "moonset": "03:04 AM",
            "moon_phase": "Waxing Gibbous",
            "moon_illumination": "79",
        }
    }
}

ERROR_RESPONSE_FROM_MOCK = {
    "error": {
        "message": "Error Text",
    }
}


@pytest.mark.asyncio
async def test_get_astronomical_data(httpx_mock):
    requested_date = datetime.datetime(day=4, month=4, year=2020)
    httpx_mock.add_response(method="GET", json=RESPONSE_FROM_MOCK)
    output = await get_astronomical_data(requested_date, "tel aviv")
    assert output['success']


@respx.mock
@pytest.mark.asyncio
async def test_astronomical_data_error_from_api():
    requested_date = datetime.datetime(day=4, month=4, year=2021)
    route = respx.get(ASTRONOMY_URL)
    route.return_value = httpx.Response(
        status.HTTP_200_OK,
        json=ERROR_RESPONSE_FROM_MOCK,
    )
    output = await get_astronomical_data(requested_date, "123")
    assert not output['success']


@respx.mock
@pytest.mark.asyncio
async def test_astronomical_exception_from_api(httpx_mock):
    requested_date = datetime.datetime.now() + datetime.timedelta(days=3)
    respx.get(ASTRONOMY_URL).mock(
        return_value=httpx.Response(status.HTTP_500_INTERNAL_SERVER_ERROR))
    output = await get_astronomical_data(requested_date, "456")
    assert not output['success']


@responses.activate
@pytest.mark.asyncio
async def test_astronomical_no_response_from_api():
    requested_date = datetime.datetime(day=11, month=1, year=2020)
    responses.add(
        responses.GET,
        ASTRONOMY_URL,
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    requests.get(ASTRONOMY_URL)
    output = await get_astronomical_data(requested_date, "789")
    assert not output['success']
