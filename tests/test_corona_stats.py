import json

import pytest
from sqlalchemy.orm.exc import NoResultFound

from app.database.models import CoronaStats
from app.internal import corona_stats

fake_data = [
    {
        "Day_Date": "2020-12-19T00:00:00.000Z",
        "vaccinated": 41,
        "vaccinated_cum": 58,
        "vaccinated_population_perc": 0,
        "vaccinated_seconde_dose": 0,
        "vaccinated_seconde_dose_cum": 0,
        "vaccinated_seconde_dose_population_perc": 0,
    },
    {
        "Day_Date": "2020-12-20T00:00:00.000Z",
        "vaccinated": 7352,
        "vaccinated_cum": 7410,
        "vaccinated_population_perc": 0.08,
        "vaccinated_seconde_dose": 0,
        "vaccinated_seconde_dose_cum": 0,
        "vaccinated_seconde_dose_population_perc": 0,
    },
    {
        "Day_Date": "2020-12-21T00:00:00.000Z",
        "vaccinated": 24863,
        "vaccinated_cum": 32273,
        "vaccinated_population_perc": 0.35,
        "vaccinated_seconde_dose": 0,
        "vaccinated_seconde_dose_cum": 0,
        "vaccinated_seconde_dose_population_perc": 0,
    },
    {
        "Day_Date": "2020-12-22T00:00:00.000Z",
        "vaccinated": 44610,
        "vaccinated_cum": 76883,
        "vaccinated_population_perc": 0.83,
        "vaccinated_seconde_dose": 0,
        "vaccinated_seconde_dose_cum": 0,
        "vaccinated_seconde_dose_population_perc": 0,
    },
]


def is_empty(session):
    res = session.query(CoronaStats).filter().count()
    return res == 0


def test_get_vacinated_data_from_db(session):
    with pytest.raises(NoResultFound):
        corona_stats.get_vacinated_data_from_db(session)


@pytest.mark.asyncio
async def test_get_vacinated_data(httpx_mock):
    test_data = json.dumps(fake_data)
    httpx_mock.add_response(method="GET", json=test_data)
    data = await corona_stats.get_vacinated_data()
    assert data


def test_save_corona_stats(session):
    test_data = (fake_data)[-1]

    corona_stats.save_corona_stats(test_data, session)

    assert is_empty(session) is False


@pytest.mark.asyncio
async def test_get_corona_stats(httpx_mock, session):
    httpx_mock.add_response(method="GET", json=fake_data)
    data = await corona_stats.get_corona_stats(session)
    assert data
    assert not is_empty(session)


def test_serialize_stats():
    stats_object = CoronaStats(
        vaccinated_second_dose_perc=100,
        vaccinated_second_dose_cum=200,
        vaccinated=0,
    )

    serialized = corona_stats.serialize_stats(stats_object)
    assert type(serialized) is dict


def test_create_stats_object():
    stats_object = fake_data[-1]

    unserialized = corona_stats.create_stats_object(stats_object)
    assert type(unserialized) is CoronaStats
