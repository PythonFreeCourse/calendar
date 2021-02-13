from collections import defaultdict
import datetime
import os
from pathlib import Path
import re
from typing import Any, Dict, Generator, List, Tuple, Union

from icalendar import Calendar
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
    VALID_FILE_EXTENSION
)
from app.routers.event import create_event

DATE_FORMAT = "%m-%d-%Y"
DATE_FORMAT2 = "%m-%d-%Y %H:%M"
DESC_EVENT = "VEVENT"
EVENT_PATTERN = re.compile(r"^(\w{" + str(EVENT_HEADER_NOT_EMPTY) + "," +
                           str(EVENT_HEADER_LIMIT) + r"}),\s(\w{0," +
                           str(EVENT_CONTENT_LIMIT) +
                           r"}),\s(\d{2}-\d{2}-\d{4})," +
                           r"\s(\d{2}-\d{2}-\d{4})(?:,\s([\w\s-]{0," +
                           str(LOCATION_LIMIT) +
                           r"}))?$")
EVENT_PATTERN2 = re.compile(r"^(\w{" + str(EVENT_HEADER_NOT_EMPTY) + "," +
                            str(EVENT_HEADER_LIMIT) + r"}),\s(\w{0," +
                            str(EVENT_CONTENT_LIMIT) +
                            r"}),\s(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})," +
                            r"\s(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})" +
                            r"(?:,\s([\w\s-]{0," + str(LOCATION_LIMIT) +
                            r"}))?$")


def is_file_size_valid(file: str, max_size: int = MAX_FILE_SIZE_MB) -> bool:
    file_size = os.stat(file).st_size / 1048576  # convert bytes to MB.
    return file_size <= max_size


def is_file_extension_valid(file: str,
                            extension: Union[str, Tuple[str, ...]]
                            = VALID_FILE_EXTENSION) -> bool:
    return file.lower().endswith(extension)


def is_file_exist(file: str) -> bool:
    return Path(file).is_file()


def change_string_to_date(date: str) -> Union[datetime.datetime, bool]:
    try:
        if ":" in date:
            date1 = datetime.datetime.strptime(date, DATE_FORMAT2)
        else:
            date1 = datetime.datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        return False
    return date1


def is_date_in_range(date: Union[str, datetime.datetime],
                     valid_dates: int = EVENT_VALID_YEARS) -> bool:
    """
    check if date is valid and in the range according to the rule we have set
    """
    now_year = datetime.datetime.now().year
    if isinstance(date, str):
        check_date = change_string_to_date(date)
        if not check_date:
            return False
    else:
        check_date = date
    return now_year - valid_dates < check_date.year < now_year + valid_dates


def is_start_day_before_end_date(start: Union[datetime.datetime, str],
                                 end: Union[datetime.datetime, str]) -> bool:
    if isinstance(start, str):
        start = change_string_to_date(start)
        end = change_string_to_date(end)
    return start <= end


def is_event_valid_duration(start: Union[datetime.datetime, str],
                            end: Union[datetime.datetime, str],
                            max_duration: int = EVENT_DURATION_LIMIT) -> bool:
    if isinstance(start, str):
        start = change_string_to_date(start)
        end = change_string_to_date(end)
    return (end - start).days < max_duration


def is_event_text_valid(row: str) -> bool:
    """Check if the row contains valid data"""
    get_values = EVENT_PATTERN.search(row)
    get_values2 = EVENT_PATTERN2.search(row)
    return get_values is not None or get_values2 is not None


def is_file_valid_to_import(file: str) -> bool:
    """
    checking before importing that the file exist, the file extension and
    the size meet the rules we have set.
    """
    return (is_file_exist(file) and is_file_extension_valid(file) and
            is_file_size_valid(file))


def is_file_valid_to_save_to_database(events: List[Dict[str, Union[str, Any]]],
                                      max_event_start_date: int
                                      = MAX_EVENTS_START_DATE) -> bool:
    """
    checking after importing that there is no larger quantity of events
    with the same date according to the rule we have set.
    """
    same_date_counter = 1
    date_n_count = defaultdict(int)
    for event in events:
        date_n_count[event["S_Date"]] += 1
        if date_n_count[event["S_Date"]] > same_date_counter:
            same_date_counter = date_n_count[event["S_Date"]]
    return same_date_counter <= max_event_start_date


def open_txt_file(txt_file: str) -> Generator[str, None, None]:
    with open(txt_file, "r") as text:
        for row in text.readlines():
            yield row


def save_calendar_content_txt(event: str, calendar_content: List) -> bool:
    """populate calendar with event content"""
    if len(event.split(", ")) == 5:
        head, content, start_date, end_date, location = event.split(", ")
        location = location.replace("\n", "")
    else:
        head, content, start_date, end_date = event.split(", ")
        end_date = end_date.replace("\n", "")
        location = None
    if (not is_date_in_range(start_date) or
            not is_date_in_range(end_date) or
            not is_start_day_before_end_date(start_date, end_date) or
            not is_event_valid_duration(start_date, end_date)):
        return False
    if re.search(r":", start_date) and re.search(r":", start_date):
        start_date = datetime.datetime.strptime(start_date, DATE_FORMAT2)
        end_date = datetime.datetime.strptime(end_date, DATE_FORMAT2)
    else:
        start_date = datetime.datetime.strptime(start_date, DATE_FORMAT)
        end_date = datetime.datetime.strptime(end_date, DATE_FORMAT)
    calendar_content.append({"Head": head,
                             "Content": content,
                             "S_Date": start_date,
                             "E_Date": end_date,
                             "Location": location})
    return True


def import_txt_file(txt_file: str) -> List[Dict[str, Union[str, Any]]]:
    calendar_content = []
    for event in open_txt_file(txt_file):
        if (not is_event_text_valid(event) or
                not save_calendar_content_txt(event, calendar_content)):
            return []
    return calendar_content


def open_ics(ics_file: str) -> Union[List, Calendar]:
    with open(ics_file, "r") as ics:
        try:
            calendar_read = Calendar.from_ical(ics.read())
        except (IndexError, ValueError) as e:
            logger.error(f"open_ics function failed error message: {e}")
            return []
    return calendar_read


def is_valid_data_event_ics(component) -> bool:
    """check if ics event data content is valid"""
    return not (str(component.get('summary')) is None or
                component.get('dtstart') is None or
                component.get('dtend') is None or
                not is_date_in_range(component.get('dtstart').dt) or
                not is_date_in_range(component.get('dtend').dt))


def save_calendar_content_ics(component, calendar_content) -> None:
    calendar_content.append({
        "Head": str(component.get('summary')),
        "Content": str(component.get('description')),
        "S_Date": component.get('dtstart').dt.replace(tzinfo=None),
        "E_Date": component.get('dtend').dt.replace(tzinfo=None),
        "Location": str(component.get('location'))
    })


def import_ics_file(ics_file: str) -> List[Dict[str, Union[str, Any]]]:
    calendar_content = []
    calendar_read = open_ics(ics_file)
    if not calendar_read:
        return []
    for component in calendar_read.walk():
        if component.name == DESC_EVENT:
            if not is_valid_data_event_ics(component):
                return []
            save_calendar_content_ics(component, calendar_content)
    return calendar_content


def save_events_to_database(events: List[Dict[str, Union[str, Any]]],
                            user_id: int,
                            session: Session) -> None:
    """insert the events into Event table"""
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
                     owner_id=owner_id)


def user_click_import(file: str, user_id: int, session: Session) -> bool:
    """
    when user choose a file and click import, we are checking the file
    and if everything is ok we will insert the data to DB
    """
    if is_file_valid_to_import(file):
        if is_file_extension_valid(file, ".ics"):
            import_file = import_ics_file(file)
        else:
            import_file = import_txt_file(file)
        if import_file and is_file_valid_to_save_to_database(import_file):
            save_events_to_database(import_file, user_id, session)
            return True
    return False
