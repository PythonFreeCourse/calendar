import json
from datetime import date, datetime
from typing import Any, Optional, Union

import geocoder

from app.config import RESOURCES_DIR


def return_shabbat_details_and_user_location() -> tuple[Any, Any]:
    """Returns times details which match to ip location,
    and the location itself.
    Used the shabbat_time_by_location JSON file, that his content is copied
    from the free API:
    'https://www.hebcal.com/shabbat?cfg=json&geonameid=295277'.
    This Json need to be update once in year.

    Returns:
        A zip number for the user location and user location by name.
    """

    location_by_ip = geocoder.ip('me')
    path = RESOURCES_DIR / "shabbat_time_by_location.json"
    with open(path, 'r', encoding="utf8") as json_file:
        shabat_details = json.load(json_file)
    for location in shabat_details:
        if (location["location"]["city"] == location_by_ip.city
                and location["location"]["cc"] == location_by_ip.country):
            return location["items"], location_by_ip


def shabbat_time_by_user_location() -> tuple[dict[str, Union[date, Any]], Any]:
    """Returns the shabbat time of the user location.

        Returns:
            Shabbat start end ending time and user location by ip.
        """
    shabat_items, location_by_ip = return_shabbat_details_and_user_location()
    for item in shabat_items:
        if "Candle lighting" in item["title"]:
            shabbat_entry = item
        if "Havdalah" in item["title"]:
            shabbat_exit = item

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
    return shabbat_limit, location_by_ip


def get_shabbat_if_date_friday(calendar_date: date) \
        -> Optional[Any]:
    """Returns shabbat start end ending time if specific date
     is Saturday, else None.

        Args:
            calendar_date: date.

        Returns:
            Shabbat start end ending time if specific date
             is Saturday and user location by ip, else None
        """
    shabbat_obj, location_by_ip = shabbat_time_by_user_location()
    if calendar_date == shabbat_obj["start_date"]:
        return shabbat_obj, location_by_ip
