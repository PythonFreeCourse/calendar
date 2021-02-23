import datetime

import pytest
import requests
import responses

from app.internal.weather_forecast import get_weather_data

HISTORY_URL = "https://visual-crossing-weather.p.rapidapi.com/history"
FORECAST_URL = "https://visual-crossing-weather.p.rapidapi.com/forecast"
RESPONSE_FROM_MOCK = {"locations": {"Tel Aviv": {"values": [
    {"mint": 6, "maxt": 17.2, "conditions": "Partially cloudy"}]}}}
ERROR_RESPONSE_FROM_MOCK = {"message": "Error Text"}
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


def test_get_forecast_weather_data(requests_mock):
    temp_date = datetime.datetime.now() + datetime.timedelta(days=2)
    response_from_mock = RESPONSE_FROM_MOCK
    response_from_mock["locations"]["Tel Aviv"]["values"][0]["datetimeStr"] = \
        temp_date.isoformat()
    requests_mock.get(FORECAST_URL, json=response_from_mock)
    output = get_weather_data(temp_date, "tel aviv")
    assert output['Status'] == 0


def test_location_not_found(requests_mock):
    requested_date = datetime.datetime(day=10, month=1, year=2020)
    requests_mock.get(HISTORY_URL, json=ERROR_RESPONSE_FROM_MOCK)
    output = get_weather_data(requested_date, "neo")
    assert output['Status'] == -1


@responses.activate
def test_historical_no_response_from_api():
    requested_date = datetime.datetime(day=11, month=1, year=2020)
    responses.add(responses.GET, HISTORY_URL, status=500)
    requests.get(HISTORY_URL)
    output = get_weather_data(requested_date, "neo")
    assert output['Status'] == -1


@responses.activate
def test_historical_exception_from_api():
    requested_date = datetime.datetime(day=12, month=1, year=2020)
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(HISTORY_URL)
    output = get_weather_data(requested_date, "neo")
    assert output['Status'] == -1


@responses.activate
def test_forecast_exception_from_api():
    requested_date = datetime.datetime.now() + datetime.timedelta(days=3)
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(FORECAST_URL)
    output = get_weather_data(requested_date, "neo")
    assert output['Status'] == -1
