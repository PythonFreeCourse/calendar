import datetime
import pytest

from app.routers.weather_forecast import get_weather_data


HISTORY_URL = "https://visual-crossing-weather.p.rapidapi.com/history"
FORECAST_URL = "https://visual-crossing-weather.p.rapidapi.com/forecast"
RESPONSE_FROM_MOCK = {"locations": {"Tel Aviv": {"values": [
    {"mint": 6, "maxt": 17.2, "conditions": "Partially cloudy"}]}}}
LOCATION_NOT_FOUND = {"message": "location not found"}
DATA_GET_WEATHER = [
    pytest.param(2020, "tel aviv", 0, marks=pytest.mark.xfail,
                 id="invalid input type"),
    pytest.param(datetime.datetime(day=4, month=4, year=2070), "tel aviv", 0,
                 marks=pytest.mark.xfail, id="year out of range"),
    pytest.param(datetime.datetime(day=4, month=4, year=2020),
                 "tel aviv", 0, id="basic historical test"),
    pytest.param(datetime.datetime(day=1, month=1, year=2030), "tel aviv", 0,
                 id="basic historical forecast test - prior in current year"),
    pytest.param(datetime.datetime(day=31, month=12, year=2030),
                 "tel aviv", 0, id="basic historical forecast test - future"),
    pytest.param(datetime.datetime(day=29, month=2, year=2024), "tel aviv",
                 0, id="basic historical forecast test"),
]


@pytest.mark.parametrize('requested_date, location, expected',
                         DATA_GET_WEATHER)
def test_get_weather_data(requested_date, location, expected, requests_mock):
    requests_mock.get(HISTORY_URL, json=RESPONSE_FROM_MOCK)
    output = get_weather_data(requested_date, location)
    assert output['Status'] == expected


@pytest.mark.xfail
def test_location_not_found(requests_mock):
    requested_date = datetime.datetime(day=15, month=1, year=2020)
    requests_mock.get(HISTORY_URL, json=LOCATION_NOT_FOUND)
    output = get_weather_data(requested_date, "neo")
    assert output['Status'] == 0


def test_get_forecast_weather_data(requests_mock):
    temp_date = datetime.datetime.now() + datetime.timedelta(days=2)
    response_from_mock = RESPONSE_FROM_MOCK
    response_from_mock["locations"]["Tel Aviv"]["values"][0]["datetimeStr"] =\
        temp_date.isoformat()
    requests_mock.get(FORECAST_URL, json=response_from_mock)
    output = get_weather_data(temp_date, "tel aviv")
    assert output['Status'] == 0
