from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import dateutil.parser
import httpx

from app import config


TOTAL_SEC_IN_HOUR = 3600
BLANK = " "
UNDERSCORE = "_"
UNPACK_ELEMENT = 0
TIMEZONES_BASE_URL = "http://worldtimeapi.org/api/timezone"
COUNTRY_TO_CONTINENT_DATA_SET_PATH = (
    f"{config.RESOURCES_PATH}/" f"country-continent.json"
)
CITY_TO_COUNTRY_DATA_SET_PATH = f"{config.RESOURCES_PATH}/world-cities.json"
TIMEZONES_COUNTRY_SUBCOUNTRY_PATH = (
    f"{config.RESOURCES_PATH}/" f"country-subcountry.json"
)

CONTINENTS = {
    "Africa",
    "America",
    "Antarctica",
    "Asia",
    "Australia",
    "Europe",
    "Indian",
    "Pacific",
}
CITY_NAME_KEY = "name"
COUNTRY_NAME_KEY_IN_CONTITNENTS = "Country_Name"
COUNTRY_NAME_KEY_IN_CITIES = "country"
SUBCOUNTRY_NAME_KEY_IN_CITIES = "subcountry"
CONTINENT_NAME_KEY = "Continent_Name"
CONTINENT = "continent"
COUNTRY = "country"
PLACE = "place"
CURRENT_TIME_KEY = "datetime"
TIMEZONE_PARTS_MAP = {CONTINENT: 0, PLACE: -1}
TIME_SCOPE_INDEX = 0
FEEDBACK_INDEX = 1
ARB_COUNTRY_TIMEZONE = -1
PATH_SEPARETOR = "/"


class MeetingTime(NamedTuple):
    time: str
    start: str
    end: str
    desirability: str


PARTS_OF_THE_DAY_FEEDBACK = [
    MeetingTime(
        time="Early Morning",
        start="05:00:00",
        end="07:59:59",
        desirability="Better not",
    ),
    MeetingTime(
        time="Morning",
        start="08:00:00",
        end="10:59:59",
        desirability="OK"
    ),
    MeetingTime(
        time="Late morning",
        start="11:00:00",
        end="11:59:59",
        desirability="OK",
    ),
    MeetingTime(
        time="Early afternoon",
        start="12:00:00",
        end="12:59:59",
        desirability="OK",
    ),
    MeetingTime(
        time="Afternoon",
        start="13:00:00",
        end="15:59:59",
        desirability="OK"
    ),
    MeetingTime(
        time="Late afternoon",
        start="16:00:00",
        end="16:59:59",
        desirability="Can be considered",
    ),
    MeetingTime(
        time="Early evening",
        start="17:00:00",
        end="18:59:59",
        desirability="Can be considered",
    ),
    MeetingTime(
        time="Evening",
        start="19:00:00",
        end="20:59:59",
        desirability="Better not",
    ),
    MeetingTime(
        time="Night",
        start="21:00:00",
        end="23:59:59",
        desirability="Better not",
    ),
    MeetingTime(
        time="Late night",
        start="00:00:00",
        end="04:59:59",
        desirability="Not possible",
    ),
]


def normalize_continent_name(continent_name: str) -> Optional[str]:
    """Normalize a given continent name to the continent name
       that appears in the timezone list.
    Args:
        continent_name (str): The given continent name.
    Returns:
        str: The normalized continent name.
    """
    for continent in CONTINENTS:
        if continent in continent_name:
            return continent
    return continent_name


def load_country_continent_data_set() -> List[Dict[str, str]]:
    """Load the country-continent data set.

    Returns:
        list: The country-continent data set.
    """
    with open(COUNTRY_TO_CONTINENT_DATA_SET_PATH) as file:
        return json.load(file)


def get_continent(country_name: str) -> Optional[str]:
    """Get the continent of a given country.
    Args:
        country_name (str): The given country name.
    Returns:
        str: The suitable continent name.
    """
    details = load_country_continent_data_set()
    for country_element in details:
        if (country_name.title() in
                country_element[COUNTRY_NAME_KEY_IN_CONTITNENTS]):
            return normalize_continent_name(
                country_element[CONTINENT_NAME_KEY]
            )


def load_city_country_data_set() -> List[Dict[str, str]]:
    """Load the city-country data set.

    Returns:
        list: The city-country data set.
    """
    with open(CITY_TO_COUNTRY_DATA_SET_PATH) as file:
        return json.load(file)


def get_country(city_name: str) -> Optional[str]:
    """Get the country of a city.
    Args:
        city_name (str): The given city name.
    Returns:
        str: The suitable country name.
    """
    details = load_city_country_data_set()
    for city_element in details:
        if city_name.title() in city_element[CITY_NAME_KEY].title():
            return city_element[COUNTRY_NAME_KEY_IN_CITIES]


def get_subcountry(city_name: str) -> Optional[str]:
    """Get the subcountry of a city.
    Args:
        city_name (str): The given city name.
    Returns:
        str: The suitable subcountry name.
    """
    details = load_city_country_data_set()
    for city_element in details:
        if city_name.title() in city_element[CITY_NAME_KEY].title():
            return city_element[SUBCOUNTRY_NAME_KEY_IN_CITIES]


async def get_api_data(url: str) -> Optional[List[Any]]:
    """Get the data from an API url.
    Args:
        url (str):  The API url.
    Returns:
        list: The data.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return resp.json()
    except (json.JSONDecodeError, httpx.HTTPError) as errh:
        print("Http Error:", errh)


async def parse_timezones_list() -> List[Tuple[str, ...]]:
    """Parse the timezones list into pairs of continent-place.
    Returns:
        list: The parsed data.
    """
    timezones = await get_api_data(TIMEZONES_BASE_URL)
    return [tuple(timezone.split(PATH_SEPARETOR)) for timezone in timezones]


async def get_timezones_parts(part: str) -> List[str]:
    """Get a given part of the timezones.
    Args:
        part (str):  The given part.
    Returns:
        list: a list of the relevant parts of the timezones list.
    """
    parse_list = await parse_timezones_list()
    return [timezone[TIMEZONE_PARTS_MAP[part]] for timezone in parse_list]


def standardize_country_or_place(place_name: str) -> Optional[str]:
    """Standardize a given country or place name to the equivalent
       name that appears in the timezone list.
    Args:
        place_name (str): The given country or place name.
    Returns:
        str: The standardized name.
    """
    if place_name:
        return place_name.replace(BLANK, UNDERSCORE).title()


async def standardize_continent(continent_name: str) -> Optional[str]:
    """Standardize a given continent name to the equivalent name that
       appears in the timezone list.
    Args:
        continent_name (str): The given continent name.
    Returns:
        str: The standardized name.
    """
    if continent_name in await get_timezones_parts(CONTINENT):
        return continent_name


async def search_timezone_by_just_place(place_name: str) -> Optional[str]:
    """Search for a timezone in the timezones list by a given place name.
    Args:
        place_name (str): The given place name.
    Returns:
        str: The suitable timezone.
    """
    res = [
        timezone
        for timezone in await get_api_data(TIMEZONES_BASE_URL)
        if place_name in timezone
    ]
    if res:
        return res[UNPACK_ELEMENT]


def generate_possible_timezone_path(
    map_hierarchy: Dict[str, Optional[str]],
) -> List[Optional[str]]:
    """Generate all possible timezone paths, given a map hierarchy
       of continent -> country -> place.
    Args:
        map_hierarchy (dict): The hierarchy details.
    Returns:
        list: The list of possible timezones.
    """
    prefix = map_hierarchy[CONTINENT]
    possibilities = [
        f"{prefix}/{map_hierarchy[COUNTRY]}",
        f"{prefix}/{map_hierarchy[PLACE]}",
    ]
    return possibilities


async def generate_possible_timezone_path_by_country(
    country: str,
    place_name: str,
) -> List[Optional[str]]:
    """Generate possible timezone paths by country.
    Args:
        country (str): The country.
        place_name (str): The place name.
    Returns:
        list: The list of possible timezones.
    """
    map_hierarchy = {
        CONTINENT: None,
        COUNTRY: None,
        PLACE: None,
    }
    possibilities = []
    map_hierarchy[COUNTRY] = country
    map_hierarchy[PLACE] = place_name
    continent = get_continent(country)
    continent = await standardize_continent(continent)
    map_hierarchy[CONTINENT] = continent
    if continent:
        return possibilities + generate_possible_timezone_path(map_hierarchy)
    elif country in await get_timezones_parts(PLACE):
        possibilities.append(await search_timezone_by_just_place(country))
        return possibilities


async def generate_possible_timezone_path_with_no_extra_data(
    place_name: str,
) -> List[Optional[str]]:
    """Generate possible timezone paths with no extra data.
    Args:
        place_name (str): The place name.
    Returns:
        list: The list of possible timezones.
    """
    possibilities = []
    place_name = standardize_country_or_place(place_name)
    if place_name in await get_timezones_parts(PLACE):
        possibilities.append(await search_timezone_by_just_place(place_name))
    return possibilities


async def get_all_possible_timezone_paths_for_given_place(
    place_name: str,
) -> Optional[List[str]]:
    """Get all possible timezone paths for given place.
    Args:
        place_name (str): The given place name.
    Returns:
        list: The list of possible timezones.
    """
    possibilities = []
    country = get_country(place_name)
    country = standardize_country_or_place(country)
    if country:
        res = await generate_possible_timezone_path_by_country(
            country, place_name
        )
        if res:
            return res
    continent = get_continent(place_name)
    continent = await standardize_continent(continent)
    if not continent:
        res = await generate_possible_timezone_path_with_no_extra_data(
            place_name
        )
        return res
    return possibilities.append(f"{continent}/{place_name}")


async def get_arbitrary_timezone_of_country(place_name: str) -> str:
    """Get an arbitrary timezone of country.
    Args:
        place_name (str): The given place name.
    Returns:
        str: The timezone.
    """
    continent_url = f"{TIMEZONES_BASE_URL}/{place_name}"
    api_data = await get_api_data(continent_url)
    timezone = api_data[ARB_COUNTRY_TIMEZONE]
    return f"{TIMEZONES_BASE_URL}/{timezone}"


def load_country_subcountry_data_set() -> List[Dict[str, str]]:
    """Load the country-csubcountry data set.

    Returns:
        list: The country-subcountry data set.
    """
    with open(TIMEZONES_COUNTRY_SUBCOUNTRY_PATH) as file:
        return json.load(file)


def get_timezone_from_subcountry(place_name: str) -> str:
    """Get the timezone from the subcountry.
    Args:
        place_name (str): The given place name.
    Returns:
        str: The timezone.
    """
    subcountry = get_subcountry(place_name)
    country = get_country(place_name)
    if subcountry:
        for timezone, details in load_country_subcountry_data_set().items():
            if (details[SUBCOUNTRY_NAME_KEY_IN_CITIES] == subcountry) or (
                details[COUNTRY] == country
            ):
                return f"{TIMEZONES_BASE_URL}/{timezone}"


async def get_timezone_path_for_given_place(place_name: str) -> Optional[str]:
    """Get a timezone path for a given place.
    Args:
        place_name (str): The given place name.
    Returns:
        str: The timezone path.
    """
    possibilities = await get_all_possible_timezone_paths_for_given_place(
        place_name
    )
    timezones = await get_api_data(TIMEZONES_BASE_URL)
    for possibility in possibilities:
        if possibility in timezones:
            return f"{TIMEZONES_BASE_URL}/{possibility}"
    # No explicit such timezones. Get an arbitrary timezone of country
    if await standardize_continent(place_name.title()):
        return await get_arbitrary_timezone_of_country(place_name)
    return get_timezone_from_subcountry(place_name)


async def get_current_time_in_place(place_name: str) -> Optional[str]:
    """Get the current time in a given place.
    Args:
        place_name (str): The given place name.
    Returns:
        str: The timezone path.
    """
    path = await get_timezone_path_for_given_place(place_name)
    if not path:
        return
    current_datetime_details = await get_api_data(path)
    current_datetime_full = current_datetime_details[CURRENT_TIME_KEY]
    current_datetime_parsed = dateutil.parser.parse(current_datetime_full)
    current_time = current_datetime_parsed.strftime("%H:%M:%S")
    return current_time


def get_part_of_day_and_feedback(time: datetime) -> Tuple[str, str]:
    """Get the part of day and a suitable feedback for a given time.
    Args:
        time (datetime): The given time.
    Returns:
        tuple: The part of day description and the feedback.
    """
    for part in PARTS_OF_THE_DAY_FEEDBACK:
        if (
            time
            >= datetime.strptime(
                part.start,
                "%H:%M:%S",
            )
            and time <= datetime.strptime(part.end, "%H:%M:%S")
        ):
            return part.time, part.desirability


def get_equivalent_time_in_place(
    time_in_place: str,
    time_part: datetime,
    wanted_time: datetime,
) -> datetime:
    """Get the equivalent time in place.
    Args:
        time_in_place (str): The time in place.
        time_part (datetime): The current time part.
        wanted_time (datetime): The wanted time here.
    Returns:
        datetime: The wanted time there.
    """
    time_in_place = datetime.strptime(time_in_place, "%H:%M:%S")
    delta_in_hours = int(
        (time_part - time_in_place).total_seconds() / TOTAL_SEC_IN_HOUR,
    )
    wanted_time_there = (
        (wanted_time + timedelta(hours=delta_in_hours)).strftime("%H:%M:%S",)
    )
    return datetime.strptime(wanted_time_there, "%H:%M:%S")


async def meeting_possibility_feedback(
    wanted_time_here: str,
    place_name: str,
) -> Optional[Tuple[str, str, str]]:
    """Get the equivalent time in a given place,
       the part of the day of that time and a feedback.
    Args:
        wanted_time_here (str): The given time as string in format HH:MM:SS.
        place_name (str): The given place name.
    Returns:
        tuple: The equivalent time in the given place,
               the part of the day of that time and a feedback.
    """
    now = datetime.now()
    now_time_part = now.strftime("%H:%M:%S")
    now_time_part = datetime.strptime(now_time_part, "%H:%M:%S")
    wanted_time_here = datetime.strptime(wanted_time_here, "%H:%M:%S")
    current_time_in_place = await get_current_time_in_place(place_name)
    if current_time_in_place:
        wanted_time_there = get_equivalent_time_in_place(
            current_time_in_place,
            now_time_part,
            wanted_time_here,
        )
        part_of_day, feedback = get_part_of_day_and_feedback(wanted_time_there)
        return (
            f"{wanted_time_there.strftime('%H')}:"
            f"{datetime.strftime(wanted_time_here, '%M:%S')}",
            part_of_day,
            feedback,
        )
