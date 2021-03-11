import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

import httpx

from app.config import RESOURCES_DIR


SHABBAT_API = 'https://www.hebcal.com/shabbat?cfg=json&geonameid='


def return_zip_code_of_user_location(location_by_ip) -> str:
    """Returns zip code from locations JSON file that match user location.

        Args:
        location_by_ip: location by ip that create with "geocoder" module.

        Returns:
        A zip code string for the user location.
    """
    path = RESOURCES_DIR / "locations.json"
    with open(path, 'r', encoding="utf8") as json_file:
        locations = json.load(json_file)
    for location in locations:
        if (location["city"] == location_by_ip.city
                and location["country"] == location_by_ip.country):
            return location["zip_number"]


def return_shabbat_times(
        shabat_items: Dict[Any, List[Dict[str, str]]]
) -> Dict[str, Union[date, Any]]:
    """Returns the shabbat time which match to ip(of the user) location.
    Used the content of this is free API:
    'https://www.hebcal.com/shabbat?cfg=json&geonameid=295277'.

        Args:
        shabat_items: dictionary of all the details about shabbat according to
        specific ip location.

        Returns:
            Shabbat start end ending time and user location by ip.
        """
    for item in shabat_items:
        if "Candle lighting" in item["title"]:
            shabbat_entry = item["date"]
        if "Havdalah" in item["title"]:
            shabbat_exit = item["date"]

    shabbat_entry_date = shabbat_entry.split("T")[0]
    shabbat_entry_hour = shabbat_entry.split("T")[1]
    shabbat_exit_date = shabbat_exit.split("T")[0]
    shabbat_exit_hour = shabbat_exit.split("T")[1]
    shabbat_limit = {
        "start_hour": shabbat_entry_hour[:5],
        "start_date": datetime.strptime(shabbat_entry_date, "%Y-%m-%d").date(),
        "end_hour": shabbat_exit_hour[:5],
        "end_date": datetime.strptime(shabbat_exit_date, "%Y-%m-%d").date(),
    }
    return shabbat_limit


async def get_shabbat_if_date_friday(calendar_date: date,
                                     location_by_ip,
                                     ) -> Optional[Dict[str, date]]:
    """Returns shabbat start end ending time if specific date is friday,
     else None.
     The function used in the free API:
     'https://www.hebcal.com/shabbat?cfg=json&geonameid=295277'.

        Args:
            calendar_date: date.
            location_by_ip: location by ip that create with "geocoder" module.

        Returns:
            Shabbat start and ending time if specific date
            is Saturday and user location by ip, else None
    """
    async with httpx.AsyncClient() as client:
        zip_code = return_zip_code_of_user_location(location_by_ip)
        shabbat_api = SHABBAT_API + zip_code
        response = await client.get(shabbat_api)
        shabat_items = response.json()['items']
        shabbat_obj = return_shabbat_times(shabat_items)
        if calendar_date == shabbat_obj["start_date"]:
            return shabbat_obj
