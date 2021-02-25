from typing import Any, Dict, Optional

import requests
from sqlalchemy.orm import Session

from app.database.models import Location


def create_location_object(location_: Dict[str, str]) -> Location:
    """Returns a Zodiac object from the dictionary data.

    Args:
        location_: A dictionary location related information.

    Returns:
        A new Location object.
    """
    return Location(
        country=location_["country"],
        city=location_["city"],
        zip_number=location_["zip_number"],
    )


def return_zip_to_location(session: Session) -> Optional[str]:
    """Returns the zip number of the user IP location that match location
     object.

    Args:
        session: The database connection.

    Returns:
        A zip number for the user location.
    """
    response = requests.get("http://ipinfo.io/json")
    if not response.ok:
        return None
    location_by_ip = response.json()
    for location in session.query(Location).all():
        if (location.city == location_by_ip["city"]
                and location.country == location_by_ip["country"]):
            return location.zip_number


def get_user_location(session: Session) -> Optional[Dict[str, Any]]:
    """Returns the user location.

        Args:
            session: The database connection.

        Returns:
            A user location.
        """
    my_location = return_zip_to_location(session)
    response = requests.get(
        f"https://www.hebcal.com/shabbat?cfg=json&geonameid={my_location}"
    )
    if response.ok:
        return response.json()
