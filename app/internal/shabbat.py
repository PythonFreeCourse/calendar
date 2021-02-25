from datetime import date, datetime
from typing import Any, Dict, Optional, Union


def get_shabbat_if_date_friday(
        shabbat_time: Dict[str, Any],
        calendar_date: date,
) -> Optional[Dict[str, Union[str, date]]]:
    """Returns shabbat start end ending time if specific date
     is Saturday, else None.

        Args:
            shabbat_time: Shabbat details.
            calendar_date: date.

        Returns:
            Shabbat start end ending time if specific date
             is Saturday, else None
        """
    shabbat_obj = shabbat_time_by_user_location(shabbat_time)
    if calendar_date == shabbat_obj["start_date"]:
        return shabbat_obj


def shabbat_time_by_user_location(
        shabbat_time: Dict[str, Any]
) -> Dict[str, Union[str, date]]:
    """Returns the shabbat time of the user location..

        Args:
            shabbat_time: Shabbat details.

        Returns:
            Shabbat start end ending time.
        """
    shabbat_entry = shabbat_time["items"][5]
    shabbat_exit = shabbat_time["items"][7]
    shabbat_entry_date = shabbat_entry["date"].split("T")[0]
    shabbat_exit_date = shabbat_entry["date"].split("T")[0]
    shabbat_limit = {
        "start_hour": shabbat_entry["title"].split(": ")[1],
        "start_date": datetime.strptime(shabbat_entry_date, "%Y-%m-%d").date(),
        "end_hour": shabbat_exit["title"].split(": ")[1],
        "end_date": datetime.strptime(shabbat_exit_date, "%Y-%m-%d").date(),
    }
    return shabbat_limit
