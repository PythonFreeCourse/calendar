import json
from unittest.mock import patch

from sqlalchemy.orm.exc import NoResultFound

from app.database.models import CoronaStats
from app.internal import corona_stats


FAKE_DATA = [{
    'Day_Date': "2020-12-19T00:00:00.000Z",
    'vaccinated': 41,
    'vaccinated_cum': 58,
    'vaccinated_population_perc': 0,
    'vaccinated_seconde_dose': 0,
    'vaccinated_seconde_dose_cum': 0,
    'vaccinated_seconde_dose_population_perc': 0
},
    {
    'Day_Date': "2020-12-20T00:00:00.000Z",
    'vaccinated': 7352,
    'vaccinated_cum': 7410,
    'vaccinated_population_perc': 0.08,
    'vaccinated_seconde_dose': 0,
    'vaccinated_seconde_dose_cum': 0,
    'vaccinated_seconde_dose_population_perc': 0
},
    {
    'Day_Date': "2020-12-21T00:00:00.000Z",
    'vaccinated': 24863,
    'vaccinated_cum': 32273,
    'vaccinated_population_perc': 0.35,
    'vaccinated_seconde_dose': 0,
    'vaccinated_seconde_dose_cum': 0,
    'vaccinated_seconde_dose_population_perc': 0
},
    {
    'Day_Date': "2020-12-22T00:00:00.000Z",
    'vaccinated': 44610,
    'vaccinated_cum': 76883,
    'vaccinated_population_perc': 0.83,
    'vaccinated_seconde_dose': 0,
    'vaccinated_seconde_dose_cum': 0,
    'vaccinated_seconde_dose_population_perc': 0
}]


def is_empty(session):
    res = (session.query(CoronaStats).
           filter().
           count()
           )
    return res == 0


def test_get_vacinated_data_from_db(session):
    try:
        corona_stats.get_vacinated_data_from_db(session)
    except NoResultFound:
        assert True
        return
    assert False


@patch('requests.get')
def test_get_vacinated_data(mock_get):
    test_data = json.dumps(FAKE_DATA)
    mock_get.return_value.ok = True
    mock_get.return_value.text = test_data
    data = corona_stats.get_vacinated_data()
    assert data


def test_save_corona_stats(session):
    test_data = (FAKE_DATA)[-1]

    corona_stats.save_corona_stats(test_data, session)

    assert is_empty(session) is False


@patch('requests.get')
def test_get_corona_stats(mock_get, session):
    test_data = json.dumps(FAKE_DATA)
    mock_get.return_value.ok = True
    mock_get.return_value.text = test_data
    assert is_empty(session)

    data = corona_stats.get_corona_stats(session)
    assert data
    assert not is_empty(session)


def test_serialize_stats():
    stats_object = CoronaStats(
        vaccinated_seconde_dose_population_perc=100,
        vaccinated_seconde_dose_cum=200,
        vaccinated=0
    )

    serialized = corona_stats.serialize_stats(stats_object)
    assert type(serialized) is dict


def test_create_stats_object():
    stats_object = FAKE_DATA[-1]

    unserialized = corona_stats.create_stats_object(stats_object)
    assert type(unserialized) is CoronaStats
