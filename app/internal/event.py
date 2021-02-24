import functools
import logging
import re
from typing import List, NamedTuple, Set, Union

from email_validator import EmailSyntaxError, validate_email
from fastapi import HTTPException
from geopy.adapters import AioHTTPAdapter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from loguru import logger
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.database.models import Country, Event
from app.resources.countries import countries

ZOOM_REGEX = re.compile(r"https://.*?\.zoom.us/[a-z]/.[^.,\b\s]+")


class Location(NamedTuple):
    # Location type hint class.
    latitude: str
    longitude: str
    name: str


def raise_if_zoom_link_invalid(vc_link):
    if ZOOM_REGEX.search(vc_link) is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="VC type with no valid zoom link",
        )


def get_invited_emails(invited_from_form: str) -> List[str]:
    invited_emails = []
    if not invited_from_form:
        return [""]
    for invited_email in invited_from_form.split(","):
        invited_email = invited_email.strip()
        try:
            validate_email(invited_email, check_deliverability=False)
        except EmailSyntaxError:
            logging.exception(
                f"{invited_email} is not a valid email address",
            )
        else:
            invited_emails.append(invited_email)

    return invited_emails


def get_uninvited_regular_emails(
    session: Session,
    owner_id: int,
    title: str,
    invited_emails: List[str],
) -> Set[str]:
    invitees_query = session.query(Event).with_entities(Event.invitees)
    similar_events_invitees = invitees_query.filter(
        Event.owner_id == owner_id,
        Event.title == title,
    ).all()
    regular_invitees = set()
    for record in similar_events_invitees:
        if record:
            regular_invitees.update(record[0].split(","))

    return regular_invitees - set(invited_emails)


def check_diffs(checked_event: Event, all_events: List[Event]):
    """Returns the repeated events and the week difference"""
    diffs = []
    for event in all_events:
        start_delta = checked_event.start - event.start
        end_delta = checked_event.end - event.end

        # The current event is before the new event and they take the same time
        if start_delta.total_seconds() > 0 and start_delta == end_delta:
            # Difference is in multiple of 7 days
            if start_delta.seconds == 0 and start_delta.days % 7 == 0:
                diffs.append(int(start_delta.days / 7))

    return diffs


def find_pattern(session, event):
    all_events_with_same_name = (
        session.query(Event)
        .filter(Event.owner_id == event.owner_id, Event.title == event.title)
        .all()
    )

    return check_diffs(event, all_events_with_same_name)


def get_messages(
    session: Session,
    event: Event,
    uninvited_contacts: Set[str],
) -> List[str]:
    messages = []
    if uninvited_contacts:
        messages.append(
            f"Forgot to invite " f'{", ".join(uninvited_contacts)} maybe?',
        )

    pattern = find_pattern(session, event)
    for weeks_diff in pattern:
        messages.append(
            f"Same event happened {weeks_diff} weeks before too. "
            f"Want to create another one {weeks_diff} after too?",
        )
    return messages


def add_countries_to_db(session: Session) -> None:
    """
    Adding all new countries to the "Country" table in the database.
    Information is based on the "countries" list.
    (The list is located in app/resources/countries.py)
    Names are described either as:
    "Country Name, City Name" or
    "Country Name" solely.
    Timezones are described as "Continent/ City Name"
    for example:
        name: Israel, Jerusalem
        timezone: Asia/Jerusalem
    """
    for country in countries:
        partial_name = country["name"]
        for capital_city in country["timezones"]:
            capital_city_name = capital_city.split("/")[-1]
            if partial_name != capital_city_name:
                name = partial_name + ", " + capital_city_name
            else:
                name = capital_city_name
            existing = session.query(Country).filter_by(name=name).first()
            if not existing:
                new_country = Country(name=name, timezone=str(capital_city))
                session.merge(new_country)
    session.commit()


@functools.lru_cache
def get_all_countries_names(session: Session) -> List[str]:
    """
    Returns a cached list of the countries names.
    """
    db_entity = session.query(Country).first()
    if not db_entity:
        add_countries_to_db(session=session)
    return session.query(Country.name).all()


async def get_location_coordinates(
    address: str,
) -> Union[Location, str]:
    """Return location coordinates and accurate
    address of the specified location."""
    try:
        async with Nominatim(
            user_agent="Pylendar",
            adapter_factory=AioHTTPAdapter,
        ) as geolocator:
            geolocation = await geolocator.geocode(address)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        logger.exception(str(e))
    else:
        if geolocation is not None:
            location = Location(
                latitude=geolocation.latitude,
                longitude=geolocation.longitude,
                name=geolocation.raw["display_name"],
            )
            return location
    return address
