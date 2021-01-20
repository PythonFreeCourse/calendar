import datetime
import pytest

from app.routers.weather_forecast import get_weather_data


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
    pytest.param(datetime.datetime(day=15, month=1, year=2020), "neo", 0,
                 marks=pytest.mark.xfail, id="location not found test"),
]


@pytest.mark.parametrize('requested_date, location, expected',
                         DATA_GET_WEATHER)
def test_get_weather_data(requested_date, location, expected):
    output = get_weather_data(requested_date, location)
    assert output['Status'] == expected


def test_get_forecast_weather_data():
    temp_date = datetime.datetime.now() + datetime.timedelta(days=2)
    output = get_weather_data(temp_date, "tel aviv")
    assert output['Status'] == 0
