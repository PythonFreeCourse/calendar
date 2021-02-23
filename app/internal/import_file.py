from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re
from typing import (
    Any, DefaultDict, Dict, Iterator, List, Optional, Tuple, Union
)

from icalendar import cal, Calendar
from loguru import logger
from sqlalchemy.orm.session import Session

from app.config import (
    EVENT_CONTENT_LIMIT,
    EVENT_DURATION_LIMIT,
    EVENT_HEADER_LIMIT,
    EVENT_HEADER_NOT_EMPTY,
    EVENT_VALID_YEARS,
    LOCATION_LIMIT,
    MAX_EVENTS_START_DATE,
    MAX_FILE_SIZE_MB,
    VALID_FILE_EXTENSION,
)
from app.routers.event import create_event

DATE_FORMAT = "%m-%d-%Y"
DATE_FORMAT2 = "%m-%d-%Y %H:%M"
DESC_EVENT = "VEVENT"

EVENT_PATTERN = re.compile(r"^(\w{" + str(int(EVENT_HEADER_NOT_EMPTY)) + "," +
                           str(EVENT_HEADER_LIMIT) + r"}),\s(\w{0," +
                           str(EVENT_CONTENT_LIMIT) +
                           r"}),\s(\d{2}-\d{2}-\d{4})," +
                           r"\s(\d{2}-\d{2}-\d{4})(?:,\s([\w\s-]{0," +
                           str(LOCATION_LIMIT) +
                           r"}))?$")

EVENT_PATTERN2 = re.compile(r"^(\w{" + str(int(EVENT_HEADER_NOT_EMPTY)) + "," +
                            str(EVENT_HEADER_LIMIT) + r"}),\s(\w{0," +
                            str(EVENT_CONTENT_LIMIT) +
                            r"}),\s(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})," +
                            r"\s(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})" +
                            r"(?:,\s([\w\s-]{0," + str(LOCATION_LIMIT) +
                            r"}))?$")


def import_events(path: str, user_id: int, session: Session) -> bool:
    """Imports events from an outside file and saves them to the database.

    For the file to be successfully imported, it must be one of the supported
    types set at VALID_FILE_EXTENSION and not pass the max size set
    at MAX_FILE_SIZE_MB.

    Args:
        path: The file path.
        user_id: The user's ID.
        session: The database connection.

    Returns:
        True if successfully saved, otherwise returns False.
    """
    if _is_file_valid_to_import(path):
        if _is_file_extension_valid(path, ".ics"):
            event_data = _get_data_from_ics_file(path)
        else:
            event_data = _get_data_from_txt_file(path)
        if event_data and _is_file_valid_to_save_to_database(event_data):
            _save_events_to_database(event_data, user_id, session)
            return True
    return False


def _is_file_valid_to_import(path: str) -> bool:
    """Whether the file is valid to be imported.

    Args:
        path: The file path.

    Returns:
        True if the file is a valid to be imported, otherwise returns False.
    """
    return (_is_file_exists(path) and _is_file_extension_valid(path)
            and _is_file_size_valid(path))


def _is_file_exists(path: str) -> bool:
    """Whether the path is a file.

    Args:
        path: The file path.

    Returns:
        True if the path is a file, otherwise returns False.
    """
    return Path(path).is_file()


def _is_file_extension_valid(
        path: str,
        extension: Union[str, Tuple[str, ...]] = VALID_FILE_EXTENSION,
) -> bool:
    """Whether the path is a valid file extension.

    Args:
        path: The file path.
        extension: Optional; A file extension suffix.
            Defaults to VALID_FILE_EXTENSION.

    Returns:
        True if the file extension is valid, otherwise returns False.
    """
    return Path(path).suffix.lower() in extension


def _is_file_size_valid(path: str, max_size: int = MAX_FILE_SIZE_MB) -> bool:
    """Whether the file size is valid.

    Args:
        path: The file path.
        max_size: Optional; The maximum file size allowed.
            Defaults to MAX_FILE_SIZE_MB.

    Returns:
        True if the file size is valid, otherwise returns False.
    """
    file_size = Path(path).stat().st_size / 1048576  # convert bytes to MB.
    return file_size <= max_size


def _get_data_from_ics_file(ics_file_path: str) -> List[Dict[str, Any]]:
    """Returns a list of event data in dictionaries from an *.ics file.

    Args:
        ics_file_path: The file path.

    Returns:
        A list of event data in dictionaries, or an empty list
        if the data is not valid.
    """
    calendar_content: List[Dict[str, Any]] = []
    calendar = _get_calendar_from_ics(ics_file_path)
    if not calendar:
        return []

    for component in calendar.walk():
        if component.name == DESC_EVENT:
            if not _is_valid_data_event_ics(component):
                return []
            _add_event_component_ics(component, calendar_content)
    return calendar_content


def _get_calendar_from_ics(ics_file_path: str) -> Optional[Calendar]:
    """Opens an *.ics file and returns a Calendar object from it.

    Args:
        ics_file_path: The file path.

    Returns:
        A Calendar object if successful, otherwise returns None.
    """
    with open(ics_file_path, "r") as ics:
        try:
            return Calendar.from_ical(ics.read())
        except (IndexError, ValueError) as e:
            logger.error(f"open_ics function failed error message: {e}")
            return None


def _is_valid_data_event_ics(component: cal.Event) -> bool:
    """Whether the ics event data is valid.

    Args:
        component: An event component.

    Returns:
        True if valid, otherwise returns False.
    """
    return not (str(component.get('summary')) is None
                or component.get('dtstart') is None
                or component.get('dtend') is None
                or not _is_date_in_range(component.get('dtstart').dt)
                or not _is_date_in_range(component.get('dtend').dt)
                )


def _add_event_component_ics(
        component: cal.Event, calendar_content: List[Dict[str, Any]]) -> None:
    """Appends event data from an *.ics file.

    Args:
        component: An event component.
        calendar_content: A list of event data.
    """
    calendar_content.append({
        "Head": str(component.get('summary')),
        "Content": str(component.get('description')),
        "S_Date": component.get('dtstart').dt.replace(tzinfo=None),
        "E_Date": component.get('dtend').dt.replace(tzinfo=None),
        "Location": str(component.get('location')),
    })


def _get_data_from_txt_file(txt_file_path: str) -> List[Dict[str, Any]]:
    """Returns a list of event data in dictionaries from a *.txt file.

    Args:
        txt_file_path: The file path.

    Returns:
        A list of event data in dictionaries, or an empty list
        if the data is not valid.
    """
    calendar_content: List[Dict[str, Any]] = []
    for event in _get_event_from_txt_file(txt_file_path):
        if not _is_event_text_valid(event):
            return []

        event_data = _get_event_data_from_text(event)

        if not _is_event_dates_valid(
                event_data["start_date"], event_data["end_date"]):
            return []

        _add_event_component_txt(event_data, calendar_content)

    return calendar_content


def _get_event_from_txt_file(txt_file: str) -> Iterator[str]:
    """Opens a *.txt file and returns a row of event data from it.

    Args:
        txt_file: The file path.

    Yields:
        A row of event data.
    """
    with open(txt_file, "r") as text:
        for row in text.readlines():
            yield row


def _is_event_text_valid(text: str) -> bool:
    """Whether the event text contains valid data.

    Args:
        text: The event text.

    Returns:
        True if valid, otherwise returns False.
    """
    get_values = EVENT_PATTERN.search(text)
    get_values2 = EVENT_PATTERN2.search(text)
    return get_values is not None or get_values2 is not None


def _get_event_data_from_text(text: str) -> Dict[str, Any]:
    """Returns the event data from the text.

    Args:
        text: The event text.

    Returns:
        A dictionary with the event data.
    """
    if len(text.split(", ")) == 5:
        head, content, start_date, end_date, location = text.split(", ")
        location = location.replace("\n", "")
    else:
        head, content, start_date, end_date = text.split(", ")
        end_date = end_date.replace("\n", "")
        location = ""

    return {
        "head": head,
        "content": content,
        "start_date": start_date,
        "end_date": end_date,
        "location": location,
    }


def _is_event_dates_valid(start: str, end: str) -> bool:
    """Whether the event dates are valid.

    Args:
        start: The start time of the event.
        end: The end time of the event.

    Returns:
        True if valid, otherwise returns False.
    """
    start_date = _convert_string_to_date(start)
    end_date = _convert_string_to_date(end)
    if start_date is None or end_date is None:
        return False

    assert start_date is not None and end_date is not None

    is_date_in_range = (_is_date_in_range(start_date)
                        and _is_date_in_range(end_date))
    is_end_after_start = _is_start_date_before_end_date(start_date, end_date)
    is_duration_valid = _is_event_duration_valid(start_date, end_date)
    return is_date_in_range and is_end_after_start and is_duration_valid


def _add_event_component_txt(
        event: Dict[str, Any], calendar_content: List[Dict[str, Any]]
) -> None:
    """Appends event data from a txt file.

    Args:
        event: An event's data.
        calendar_content: A list of event data.
    """
    if ":" in event["start_date"] and ":" in event["start_date"]:
        start_date = datetime.strptime(event["start_date"], DATE_FORMAT2)
        end_date = datetime.strptime(event["end_date"], DATE_FORMAT2)
    else:
        start_date = datetime.strptime(event["start_date"], DATE_FORMAT)
        end_date = datetime.strptime(event["end_date"], DATE_FORMAT)

    calendar_content.append({
        "Head": event["head"],
        "Content": event["content"],
        "S_Date": start_date,
        "E_Date": end_date,
        "Location": event["location"],
    })


def _convert_string_to_date(string_date: str) -> Optional[datetime]:
    """Returns a datetime object from a date written as a text string.

    Args:
        string_date: The date as a text string.

    Returns:
        A datetime date.
    """
    try:
        if ":" in string_date:
            date = datetime.strptime(string_date, DATE_FORMAT2)
        else:
            date = datetime.strptime(string_date, DATE_FORMAT)
    except ValueError:
        return None
    return date


def _is_date_in_range(
        date: datetime, year_range: int = EVENT_VALID_YEARS
) -> bool:
    """Whether the date is in range.

    The range should be between the current year - the EVENT_VALID_YEARS
    and the current year + EVENT_VALID_YEARS.
    Currently EVENT_VALID_YEARS is set to 20 years, meaning a valid date cannot
    be more than 20 years in the past or 20 years in the future.

    Args:
        date: The date to validate.
        year_range: Optional; The valid year range.
            Defaults to EVENT_VALID_YEARS.

    Returns:
        True if valid, otherwise returns False.
    """
    current_year = datetime.now().year
    return current_year - year_range < date.year < current_year + year_range


def _is_start_date_before_end_date(start: datetime, end: datetime) -> bool:
    """Whether the start date is before the end date.

    Args:
        start: The start date of an event.
        end: The end date of an event.

    Returns:
        True if valid, otherwise returns False.
    """
    return start <= end


def _is_event_duration_valid(
        start: datetime, end: datetime, max_days: int = EVENT_DURATION_LIMIT
) -> bool:
    """Whether an event duration is valid.

    Args:
        start: The start date of an event.
        end: The end date of an event.
        max_days: Optional; The maximum number of days an event can be held.
            Defaults to EVENT_DURATION_LIMIT.

    Returns:
        True if valid, otherwise returns False.
    """
    return (end - start).days < max_days


def _is_file_valid_to_save_to_database(
        events: List[Dict[str, Any]],
        max_event_start_date: int = MAX_EVENTS_START_DATE,
) -> bool:
    """Whether the number of events starting on the same date is valid.

    The number of events starting on the same date cannot be greater than the
    maximum number of events allowed to start on the same day in the settings.
    The default value is set in MAX_EVENTS_START_DATE.

    Args:
        events: A list of events.
        max_event_start_date: Optional; The maximum number of events allowed
            to start on the same day.
            Defaults to MAX_EVENTS_START_DATE.

    Returns:
        True if valid, otherwise returns False.
    """
    same_date_counter = 1
    dates: DefaultDict[datetime, int] = defaultdict(int)
    for event in events:
        dates[event["S_Date"]] += 1
        if dates[event["S_Date"]] > same_date_counter:
            same_date_counter = dates[event["S_Date"]]
    return same_date_counter <= max_event_start_date


def _save_events_to_database(
        events: List[Dict[str, Any]], user_id: int, session: Session
) -> None:
    """Inserts the events into the Event table.

    Args:
        events: A list of events.
        user_id: The user's ID.
        session: The database connection.
    """
    for event in events:
        title = event["Head"]
        content = event["Content"]
        start = event["S_Date"]
        end = event["E_Date"]
        location = event["Location"]
        owner_id = user_id
        create_event(db=session,
                     title=title,
                     content=content,
                     start=start,
                     end=end,
                     location=location,
                     owner_id=owner_id,
                     )
