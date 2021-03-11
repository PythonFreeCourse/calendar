import json
from datetime import date

import geocoder
import pytest

from app.internal import shabbat

FAKE_SHABBAT_DATA = {
    "items":
        [
            {"title": "Fast begins"},
            {"title": "Ta'anit Esther"},
            {"title": "Fast ends"},
            {"title": "Erev Purim"},
            {"title": "Purim"},
            {
                "title": "Candle lighting: 17:15",
                "date": "2021-02-26T17:15:00+02:00",
                "category": "candles",
                "title_orig": "Candle lighting",
                "hebrew": "הדלקת נרות",
            },
            {"title": "Parashat Tetzaveh"},
            {
                "title": "Havdalah: 18:11",
                "date": "2021-02-27T18:11:00+02:00",
                "category": "havdalah",
                "title_orig": "Havdalah",
                "hebrew": "הבדלה",
            },
        ]
}
FRIDAY = date(2021, 2, 26)
BAD_DAY = date(2021, 2, 27)


@pytest.mark.asyncio
async def test_return_if_date_is_friday(httpx_mock):
    location_by_ip = geocoder.ip('me')
    test_data = json.dumps(FAKE_SHABBAT_DATA)
    httpx_mock.add_response(method="GET", json=test_data)
    result = await shabbat.get_shabbat_if_date_friday(FRIDAY, location_by_ip)
    assert result


@pytest.mark.asyncio
async def test_return_if_date_is_not_friday(httpx_mock):
    location_by_ip = geocoder.ip('me')
    test_data = json.dumps(FAKE_SHABBAT_DATA)
    httpx_mock.add_response(method="GET", json=test_data)
    result = await shabbat.get_shabbat_if_date_friday(BAD_DAY, location_by_ip)
    assert result is None


def test_return_shabbat_times():
    result = shabbat.return_shabbat_times(FAKE_SHABBAT_DATA)
    assert result["start_hour"] == "17:15"
    assert result["end_hour"] == "18:11"


def test_return_zip_code_of_user_location():
    location_by_ip = geocoder.ip('me')
    result = shabbat.return_zip_code_of_user_location(location_by_ip)
    assert result
