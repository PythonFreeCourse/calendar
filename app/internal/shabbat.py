import json
from datetime import date, datetime
from typing import Any, Dict, Optional, Union

import geocoder


def return_zip_to_ip_location() -> Optional[str]:
    """Returns the zip number of the user IP location that match location
     object.

    Returns:
        A zip number for the user location.
    """

    location_by_ip = geocoder.ip('me')
    path = r'../app/resources/shabbat_time_by_location.json'
    with open(path, 'r') as json_file:
        shabat_details = json.load(json_file)
    for location in shabat_details:
        if (location["location"]["city"] == location_by_ip.city
                and location["location"]["cc"] == location_by_ip.country):
            return location["items"], location_by_ip


def shabbat_time_by_user_location() -> Dict[str, Union[str, date]]:
    """Returns the shabbat time of the user location.

        Returns:
            Shabbat start end ending time.
        """
    shabat_items, location_by_ip = return_zip_to_ip_location()
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
        -> Optional[Dict[str, Union[str, date]], Any]:
    """Returns shabbat start end ending time if specific date
     is Saturday, else None.

        Args:
            shabbat_time: Shabbat details.
            calendar_date: date.

        Returns:
            Shabbat start end ending time if specific date
             is Saturday, else None
        """
    shabbat_obj, location_by_ip = shabbat_time_by_user_location()
    if calendar_date == shabbat_obj["start_date"]:
        return shabbat_obj, location_by_ip
