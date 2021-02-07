import io

import sys

from app.routers.world_clock import generate_possible_timezone_path,\
    get_all_possible_timezone_paths_for_given_place,\
    get_api_data, get_continent, get_country, \
    get_current_time_in_place, get_part_of_day_and_feedback,\
    get_subcountry,\
    get_timezone_path_for_given_place, get_timezones_parts,\
    meeting_possibility_feedback,\
    normalize_continent_name,\
    parse_timezones_list, search_timezone_by_just_place,\
    standardize_continent,\
    standardize_country_or_place, TIMEZONES_BASE_URL

import pytest
import requests

from unittest.mock import patch
from unittest import mock
from unittest.mock import patch

from datetime import datetime
from requests import HTTPError


def test_api_http_error():
    with patch('app.routers.world_clock.requests.get',
               side_effect=requests.exceptions.HTTPError):
        assert not get_api_data(TIMEZONES_BASE_URL)


def test_api_connection_error():
    with patch('app.routers.world_clock.requests.get',
               side_effect=requests.exceptions.ConnectionError):
        assert not get_api_data(TIMEZONES_BASE_URL)


def test_api_timeout_error():
    with patch('app.routers.world_clock.requests.get',
               side_effect=requests.exceptions.Timeout):
        assert not get_api_data(TIMEZONES_BASE_URL)


def test_api_request_exception():
    with patch('app.routers.world_clock.requests.get',
               side_effect=requests.exceptions.RequestException):
        assert not get_api_data(TIMEZONES_BASE_URL)


def test_get_api_data():
    timezones_data = get_api_data(TIMEZONES_BASE_URL)
    for timezone in timezones_data:
        assert type(timezone) == type('timezone')


items_details = [
    ('Africa', 'Africa'),
    ('South America', 'America'),
    ('Oceania', 'Oceania'),
]

@pytest.mark.parametrize('continent_name, normalized_continent',
                         items_details)
def test_normalize_continent_name(continent_name, normalized_continent):
    assert normalize_continent_name(continent_name) == normalized_continent


items_details = [
    ('Africa', 'Africa'),
    ('ISrael', 'Asia'),
    ('Bermuda', 'America'),
    ('Australia', 'Oceania'),
    ('Narnia', None),
]


@pytest.mark.parametrize('country_name, continent', items_details)
def test_get_continent(country_name, continent):
    assert get_continent(country_name) == continent


items_details = [
    ('rio de janeiro', 'Brazil'),
    ('pago pago', 'American Samoa'),
    ('jerusalem', 'Israel'),
    ('new york', 'United States'),
    ('Narnia', None),
]


@pytest.mark.parametrize('city_name, country', items_details)
def test_get_country(city_name, country):
    assert get_country(city_name) == country


items_details = [
    ('HAIFA', 'Haifa'),
    ('Binghamton', 'New York'),
    ('Ramat Gan', 'Tel Aviv'),
]


@pytest.mark.parametrize('city_name, subcountry', items_details)
def test_get_subcountry(city_name, subcountry):
    assert get_subcountry(city_name) == subcountry


def test_parse_timezones_list():
    assert ('Africa', 'Abidjan') in parse_timezones_list()


items_details = [
    ('place', 'Abidjan'),
    ('continent', 'Africa'),
]


@pytest.mark.parametrize('param, res', items_details)
def test_get_timezones_parts(param, res):
    assert res == get_timezones_parts(param)[0]


items_details = [
    ('Broken Hill', 'Broken_Hill'),
    (None, None),
]


@pytest.mark.parametrize('place, standardized_place', items_details)
def test_standardize_country_or_place(place, standardized_place):
    assert standardize_country_or_place(place) == standardized_place


items_details = [
    ('Africa', 'Africa'),
    ('South America', None),
    ('America', 'America'),
    ('Oceania', None),
]


@pytest.mark.parametrize('continent_name, standardized_continent',
                         items_details)
def test_standardize_continent(continent_name, standardized_continent):
    assert standardize_continent(continent_name) == standardized_continent


items_details = [
    ('anjdk', None),
    ('Jerusalem', 'Asia/Jerusalem'),
]


@pytest.mark.parametrize('place_name, timezone', items_details)
def test_search_timezone_by_just_place(place_name, timezone):
    assert search_timezone_by_just_place(place_name) == timezone


items_details = [
    ({'continent': 'Asia', 'country': 'Israel', 'place': 'Haifa', },
     ['Asia/Israel', 'Asia/Haifa']),
]


@pytest.mark.parametrize('map, possibilities', items_details)
def test_generate_possible_timezone_path(map, possibilities):
    assert generate_possible_timezone_path(map) == possibilities


items_details = [
    ('pago pago', ['Pacific/Pago_Pago']),
    ('Nauru', ['Pacific/Nauru']),
    ('Yaren', ['Pacific/Nauru']),
    ('Haifa', ['Asia/Israel', 'Asia/Haifa']),
    ('Australia', None),
]


@pytest.mark.parametrize('place_name, possibilities', items_details)
def test_get_all_possible_timezone_paths_for_given_place(place_name,
                                                         possibilities):
    assert get_all_possible_timezone_paths_for_given_place(place_name) ==\
           possibilities


items_details = [
    ('pago pago',
     'http://worldtimeapi.org/api/timezone/Pacific/Pago_Pago'),
    ('Nauru', 'http://worldtimeapi.org/api/timezone/Pacific/Nauru'),
    ('Yaren', 'http://worldtimeapi.org/api/timezone/Pacific/Nauru'),
    ('Haifa', 'http://worldtimeapi.org/api/timezone/Asia/Jerusalem'),
    ('Australia',
     'http://worldtimeapi.org/api/timezone/Australia/Sydney'),
]


@pytest.mark.parametrize('place_name, path', items_details)
def test_get_timezone_path_for_given_place(place_name, path):
    assert get_timezone_path_for_given_place(place_name) == path


def test_get_current_time_in_place():
    current_time = get_current_time_in_place('pago pago')
    assert len(current_time) == 8


def test_get_part_of_day_and_feedback():
    assert get_part_of_day_and_feedback(datetime.strptime(
        '02:42:45', '%H:%M:%S')) == ('Late night', 'Not possible')


items_details = [
    ('22:22:12', 'Haifa', ('22:22:12', 'Night', 'Better not')),
    ('22:22:12','Australia', ('12:22:12', 'Early afternoon', 'OK')),
]


@pytest.mark.parametrize('time_str, place_name, res', items_details)
def test_meeting_possibility_feedback(time_str, place_name, res):
    assert meeting_possibility_feedback(time_str, place_name) == res
