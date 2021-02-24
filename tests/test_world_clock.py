from datetime import datetime
import pytest

import httpx
import respx

from app.internal.world_clock import (
    generate_possible_timezone_path,
    generate_possible_timezone_path_by_country,
    get_all_possible_timezone_paths_for_given_place,
    get_api_data,
    get_continent,
    get_country,
    get_arbitrary_timezone_of_country,
    get_current_time_in_place,
    get_part_of_day_and_feedback,
    get_subcountry,
    get_timezone_from_subcountry,
    get_timezone_path_for_given_place,
    get_timezones_parts,
    load_city_country_data_set,
    load_country_continent_data_set,
    load_country_subcountry_data_set,
    meeting_possibility_feedback,
    normalize_continent_name,
    parse_timezones_list,
    search_timezone_by_just_place,
    standardize_continent,
    standardize_country_or_place,
    TIMEZONES_BASE_URL,
)


@respx.mock
@pytest.mark.asyncio
async def test_api_http_error():
    respx.get(TIMEZONES_BASE_URL).mock(return_value=httpx.Response(500))
    output = await get_api_data(TIMEZONES_BASE_URL)
    assert not output


@pytest.mark.asyncio
async def test_get_api_data():
    timezones_data = await get_api_data(TIMEZONES_BASE_URL)
    assert timezones_data


items_details = [
    ("Africa", "Africa"),
    ("South America", "America"),
    ("Oceania", "Oceania"),
]


@pytest.mark.parametrize("continent_name, normalized_continent", items_details)
def test_normalize_continent_name(continent_name, normalized_continent):
    assert normalize_continent_name(continent_name) == normalized_continent


items_details = [
    ("Bermuda", "America"),
    ("Narnia", None),
]


@pytest.mark.parametrize("country_name, continent", items_details)
def test_get_continent(country_name, continent):
    assert get_continent(country_name) == continent


def test_load_city_country_data_set():
    assert load_city_country_data_set()


def test_load_country_continent_data_set():
    assert load_country_continent_data_set()


def test_load_country_subcountry_data_set():
    assert load_country_subcountry_data_set()


items_details = [
    ("rio de janeiro", "Brazil"),
    ("pago pago", "American Samoa"),
    ("jerusalem", "Israel"),
    ("Narnia", None),
]


@pytest.mark.parametrize("city_name, country", items_details)
def test_get_country(city_name, country):
    assert get_country(city_name) == country


items_details = [
    ("Israel", "Jerusalem", ["Asia/Israel", "Asia/Jerusalem"]),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("country, place, res", items_details)
async def test_generate_possible_timezone_path_by_country(country, place, res):
    assert await generate_possible_timezone_path_by_country(country, place) == res


items_details = [
    ("Australia", "http://worldtimeapi.org/api/timezone/Australia/Sydney"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("country, res", items_details)
async def test_get_arbitrary_timezone_of_country(country, res):
    assert await get_arbitrary_timezone_of_country(country) == res


items_details = [
    ("Haifa", "http://worldtimeapi.org/api/timezone/Asia/Jerusalem"),
]


@pytest.mark.parametrize("place, res", items_details)
def test_get_timezone_from_subcountry(place, res):
    assert get_timezone_from_subcountry(place) == res


items_details = [
    ("HAIFA", "Haifa"),
    ("Binghamton", "New York"),
    ("Ramat Gan", "Tel Aviv"),
]


@pytest.mark.parametrize("city_name, subcountry", items_details)
def test_get_subcountry(city_name, subcountry):
    assert get_subcountry(city_name) == subcountry


@pytest.mark.asyncio
async def test_parse_timezones_list():
    assert ("Africa", "Abidjan") in await parse_timezones_list()


items_details = [
    ("place", "Abidjan"),
    ("continent", "Africa"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("param, res", items_details)
async def test_get_timezones_parts(param, res):
    time_zone_parts = await get_timezones_parts(param)
    assert res == time_zone_parts[0]


items_details = [
    ("Broken Hill", "Broken_Hill"),
    (None, None),
]


@pytest.mark.parametrize("place, standardized_place", items_details)
def test_standardize_country_or_place(place, standardized_place):
    assert standardize_country_or_place(place) == standardized_place


items_details = [
    ("Africa", "Africa"),
    ("South America", None),
    ("America", "America"),
    ("Oceania", None),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("continent_name, standardized_continent", items_details)
async def test_standardize_continent(continent_name, standardized_continent):
    assert await standardize_continent(continent_name) == standardized_continent


items_details = [
    ("anjdk", None),
    ("Jerusalem", "Asia/Jerusalem"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("place_name, timezone", items_details)
async def test_search_timezone_by_just_place(place_name, timezone):
    assert await search_timezone_by_just_place(place_name) == timezone


items_details = [
    (
        {
            "continent": "Asia",
            "country": "Israel",
            "place": "Haifa",
        },
        ["Asia/Israel", "Asia/Haifa"],
    ),
]


@pytest.mark.parametrize("map, possibilities", items_details)
def test_generate_possible_timezone_path(map, possibilities):
    assert generate_possible_timezone_path(map) == possibilities


items_details = [
    ("pago pago", ["Pacific/Pago_Pago"]),
    ("Nauru", ["Pacific/Nauru"]),
    ("Yaren", ["Pacific/Nauru"]),
    ("Haifa", ["Asia/Israel", "Asia/Haifa"]),
    ("Australia", []),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("place_name, possibilities", items_details)
async def test_get_all_possible_timezone_paths_for_given_place(
    place_name, possibilities,
):
    assert (
        await get_all_possible_timezone_paths_for_given_place(place_name)
        == possibilities
    )


items_details = [
    ("pago pago", "http://worldtimeapi.org/api/timezone/Pacific/Pago_Pago"),
    ("Nauru", "http://worldtimeapi.org/api/timezone/Pacific/Nauru"),
    ("Yaren", "http://worldtimeapi.org/api/timezone/Pacific/Nauru"),
    ("Haifa", "http://worldtimeapi.org/api/timezone/Asia/Jerusalem"),
    ("Australia", "http://worldtimeapi.org/api/timezone/Australia/Sydney"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("place_name, path", items_details)
async def test_get_timezone_path_for_given_place(place_name, path):
    assert await get_timezone_path_for_given_place(place_name) == path


@pytest.mark.asyncio
async def test_get_current_time_in_place():
    current_time = await get_current_time_in_place("pago pago")
    assert len(current_time) == 8


def test_get_part_of_day_and_feedback():
    assert get_part_of_day_and_feedback(datetime.strptime("02:42:45", "%H:%M:%S")) == (
        "Late night",
        "Not possible",
    )


items_details = [
    (
        "22:22:12",
        "Haifa",
        [("20:22:12", "Evening", "Better not"), ("21:22:12", "Night", "Better not")],
    ),
    (
        "22:22:12",
        "Australia",
        [("10:22:12", "Morning", "OK"), ("11:22:12", "Late morning", "OK")],
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("time_str, place_name, res", items_details)
async def test_meeting_possibility_feedback(time_str, place_name, res):
    assert await meeting_possibility_feedback(time_str, place_name) in res
