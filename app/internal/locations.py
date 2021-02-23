import requests
from typing import Dict

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
        country=location_['country'],
        city=location_['city'],
        zip_number=location_['zip_number'],
    )


def return_zip_to_location(session: Session) -> str:
    """Returns the zip number of the user IP location that match location object.

    Args:
        session: The database connection.

    Returns:
        A zip number for the user location.
    """
    ip_and_location = requests.get('http://ipinfo.io/json').json()
    for location in session.query(Location).all():
        if location.city == ip_and_location['city'] and \
                location.country == ip_and_location['country']:
            return location.zip_number


def get_user_location(session: Session) -> str:
    """Returns the user location.

        Args:
            session: The database connection.

        Returns:
            A user location string.
        """
    my_location = return_zip_to_location(session)
    location_details = requests.get(f"https://www.hebcal.com/shabbat?cfg=json&geonameid={my_location}")
    return location_details.json()
