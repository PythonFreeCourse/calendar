import datetime
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple, Union

from icalendar import Calendar

from app.database.models import Event
from app.database.database import SessionLocal


NUM_OF_VALUES = 4  # Event contains head, content, start_date and end_date.
MAX_FILE_SIZE_MB = 5  # 5MB
VALID_FILE_EXTENSION = (".txt", ".csv", ".ics")  # Can import only these files.
VALID_YEARS = 20  # Events must be within 20 years range from the current year.
EVENT_HEADER_NOT_EMPTY = 1  # 1- for not empty, 0- for empty.
EVENT_HEADER_LIMIT = 50  # Max characters for event header.
EVENT_CONTENT_LIMIT = 500  # Max characters for event characters.
MAX_EVENTS_START_DATE = 10  # Max Events with the same start date.


def is_file_size_valid(file: str, max_size: int = MAX_FILE_SIZE_MB) -> bool:
    file_size = os.stat(file).st_size / 1048576  # convert bytes to MB.
    return file_size <= max_size


def is_file_extension_valid(file: str,
                            extension: Union[str, Tuple[str, ...]]
                            = VALID_FILE_EXTENSION) -> bool:
    return file.lower().endswith(extension)


def is_file_exist(file: str) -> bool:
    if Path(file).is_file():
        return True
    return False


def is_date_in_range(date: Union[str, datetime.datetime],
                     valid_dates: int = VALID_YEARS) -> bool:
    """
    check if date is valid and in the range according to the rule we have set
    """
    now_year = datetime.datetime.now().year
    if isinstance(date, str):
        try:
            check_date = datetime.datetime.strptime(date, "%m-%d-%Y")
        except ValueError:
            return False
    else:
        check_date = date
    if check_date.year > now_year + valid_dates or \
       check_date.year < now_year - valid_dates:
        return False
    return True


def is_event_text_valid(row: str) -> bool:
    """Check if the row contains valid data"""
    get_values = re.findall(r"^(\w{" + str(EVENT_HEADER_NOT_EMPTY) + "," +
                            str(EVENT_HEADER_LIMIT) + r"}),\s(\w{0," +
                            str(EVENT_CONTENT_LIMIT) +
                            r"}),\s(\d{2}-\d{2}-\d{4})," +
                            r"\s(\d{2}-\d{2}-\d{4})$", row)
    if get_values:
        if len(get_values[0]) == NUM_OF_VALUES:
            return True
    return False


def is_file_valid_to_import(file: str) -> bool:
    """
    checking before importing that the file exist, the file extension and
    the size meet the rules we have set.
    """
    if not is_file_exist(file):
        return False
    if not is_file_extension_valid(file):
        return False
    if not is_file_size_valid(file):
        return False
    return True


def is_file_valid_to_save_to_database(events: List[Dict[str, Union[str, Any]]],
                                      max_event_start_date: int
                                      = MAX_EVENTS_START_DATE) -> bool:
    """
    checking after importing that there is no larger quantity of events
    with the same date according to the rule we have set.
    """
    same_date_counter = 1
    date_n_count = {}
    for event in events:
        if event["S_Date"] in date_n_count:
            date_n_count[event["S_Date"]] += 1
            if date_n_count[event["S_Date"]] > same_date_counter:
                same_date_counter = date_n_count[event["S_Date"]]
        else:
            date_n_count[event["S_Date"]] = 1
    return same_date_counter <= max_event_start_date


def import_txt_file(txt_file: str) -> List[Dict[str, Union[str, Any]]]:
    calendar_content = []
    with open(txt_file, "r") as text:
        events = text.readlines()
    for event in events:
        if not is_event_text_valid(event):
            return list()
        head, content, start_date, end_date = event.split(", ")
        if not is_date_in_range(start_date) or \
           not is_date_in_range(end_date.replace("\n", "")):
            return list()
        start_date = datetime.datetime.strptime(start_date, "%m-%d-%Y")
        end_date = datetime.datetime.strptime(end_date.replace("\n", ""),
                                              "%m-%d-%Y")
        calendar_content.append({"Head": head,
                                 "Content": content,
                                 "S_Date": start_date,
                                 "E_Date": end_date})
    return calendar_content


def import_ics_file(ics_file: str) -> List[Dict[str, Union[str, Any]]]:
    calendar_content = []
    with open(ics_file, "r") as ics:
        try:
            calendar_read = Calendar.from_ical(ics.read())
        except (IndexError, ValueError):
            return list()
        for component in calendar_read.walk():
            if component.name == "VEVENT":
                if str(component.get('summary')) is None or \
                   component.get('dtstart') is None or \
                   component.get('dtend') is None or \
                   not is_date_in_range(component.get('dtstart').dt) or \
                   not is_date_in_range(component.get('dtend').dt):
                    return list()
                else:
                    calendar_content.append({
                        "Head": str(component.get('summary')),
                        "Content": str(component.get('description')),
                        "S_Date": component.get('dtstart').dt
                        .replace(tzinfo=None),
                        "E_Date": component.get('dtend').dt
                        .replace(tzinfo=None)
                    })
    return calendar_content


def save_events_to_database(events: List[Dict[str, Union[str, Any]]],
                            user_id: int,
                            session: SessionLocal = SessionLocal()) -> None:
    """insert the events into Event table"""
    for event in events:
        event = Event(
            title=event["Head"],
            content=event["Content"],
            start=event["S_Date"],
            end=event["E_Date"],
            owner_id=user_id
        )
        session.add(event)
    session.commit()
    session.close()


def user_click_import(file: str, user_id: int,
                      session: SessionLocal = SessionLocal()) -> str:
    """
    when user choose a file and click import, we are checking the file
    and if everything is ok we will insert the data to DB
    """
    if is_file_valid_to_import(file):
        if is_file_extension_valid(file, ".ics"):
            import_file = import_ics_file(file)
        else:
            import_file = import_txt_file(file)
        if import_file:
            if is_file_valid_to_save_to_database(import_file):
                save_events_to_database(import_file, user_id, session)
                return True
    return False
