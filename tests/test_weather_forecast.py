from datetime import datetime, timedelta
import pytest

from app.weather_forecast import get_weather_data


DATA_GET_WEATHER = [
    pytest.param(4, "d", 2020, "tel aviv", 0, marks=pytest.mark.xfail, id="ivalid input type"),
    pytest.param(4, 4, 2020, "tel aviv", 0, id="basic historical test"),
    pytest.param(4, 4, 2070, "tel aviv", 0, marks=pytest.mark.xfail, id="year out of range"),
    pytest.param(1, 1, 2030, "tel aviv", 0, id="basic historical forecast test - prior in current year"),
    pytest.param(31, 12, 2030, "tel aviv", 0, id="basic historical forecast test - future"),
    pytest.param(15, 1, 2020, "neo", 0, marks=pytest.mark.xfail, id="location not found test"),
    pytest.param(32, 1, 2020, "tel aviv", 0, marks=pytest.mark.xfail, id="invalid date"),
    pytest.param(29, 2, 2024, "tel aviv", 0, id="basic historical forecast test"),
]


@pytest.mark.parametrize('day, month, year, location, expected', DATA_GET_WEATHER)
def test_get_weather_data(day, month, year, location, expected):
    output = get_weather_data(day, month, year, location)
    assert output['Status'] == expected


def test_get_forecast_weather_data():
    temp_date = datetime.now() + timedelta(days=1)
    output = get_weather_data(temp_date.day, temp_date.month, temp_date.year, "tel aviv")
    assert output['Status'] == 0

# pytest.param(15, 1, 2021, "tel aviv", 0, id="basic forecast test"),
