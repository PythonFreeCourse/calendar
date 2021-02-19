from app.database.models import Quote, Zodiac
from app.internal import json_data_loader


def get_objects_amount(session, table):
    return session.query(table).count()


def test_load_daily_quotes(session):
    json_data_loader.load_to_database(session)
    assert get_objects_amount(session, Quote) > 0


def test_load_zodiacs(session):
    json_data_loader.load_to_database(session)
    assert get_objects_amount(session, Zodiac) > 0


# tests for basic functionality of the json data loader
def test_load_data_with_json_value_error(mocker, session):
    mocker.patch('json.load', side_effect=ValueError)
    json_data_loader.load_to_database(session)
    assert get_objects_amount(session, Quote) == 0


def test_data_not_load_twice_to_db(session):
    json_data_loader.load_to_database(session)
    first_quotes_amount = get_objects_amount(session, Quote)
    json_data_loader.load_to_database(session)
    assert first_quotes_amount == get_objects_amount(session, Quote)
