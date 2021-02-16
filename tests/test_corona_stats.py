import json
from unittest.mock import patch

from sqlalchemy.orm.exc import NoResultFound

from app.database.models import CoronaStats
from app.internal import corona_stats


def is_empty(session):
    try:
        corona_stats.get_vacinated_data_from_db(session)
    except NoResultFound:
        return True
    return False


def test_get_vacinated_data_from_db(session):
    try:
        corona_stats.get_vacinated_data_from_db(session)
    except NoResultFound:
        assert True
        return
    assert False


@patch('requests.get')
def test_get_vacinated_data(mock_get):
    fake_data = [{"this is test": "test"}]
    test_data = json.dumps(fake_data)
    mock_get.return_value.ok = True
    mock_get.return_value.text = test_data
    data = corona_stats.get_vacinated_data()
    assert data is not None


def test_get_corona_stats(session):
    assert is_empty(session) is True

    data = corona_stats.get_corona_stats(session)
    assert data is not None

    assert is_empty(session) is False


def test_serialize_stats():
    stats_object = CoronaStats(
        vaccinated_seconde_dose_population_perc=100,
        vaccinated_seconde_dose_cum=200,
        vaccinated=0
    )

    serialized = corona_stats.serialize_stats(stats_object)
    assert type(serialized) is dict


def test_create_stats_object():
    stats_object = {
        'Day_Date':  "2020-12-20T00:00:00.000Z",
        'vaccinated_seconde_dose_population_perc': 100,
        'vaccinated_seconde_dose_cum': 200,
        'vaccinated': 0
    }

    unserialized = corona_stats.create_stats_object(stats_object)
    assert type(unserialized) is CoronaStats
