import datetime
import os
import re
from typing import Any, Dict, List, Tuple, Union

from icalendar import Calendar

from app.database.models import Event
from app.database.database import SessionLocal


NUM_OF_VALUES = 3  # Event contains head, content and date.
MAX_FILE_SIZE_MB = 5  # 5MB
VALID_FILE_EXTENSION = (".txt", ".csv", ".ics")  # Can import only these files.
VALID_YEARS = 20  # Events must be within 20 years range from the current year.
EVENT_HEADER_NOT_EMPTY = 1  # 1- for not empty, 0- for empty.
EVENT_HEADER_LIMIT = 50  # Max characters for event header.
EVENT_CONTENT_LIMIT = 500  # Max characters for event characters.
MAX_EVENTS_START_DATE = 10  # Max Events with the same start date.


def check_file_size(file: str, max_size: int = MAX_FILE_SIZE_MB) -> bool:
    file_size = os.stat(file).st_size / 1048576  # convert bytes to MB.
    return file_size <= max_size


def check_file_extension(file: str,
                         extension: Union[str, Tuple[str, ...]]
                         = VALID_FILE_EXTENSION) -> bool:
    return file.lower().endswith(extension)


def is_file_exist(file: str) -> bool:
    try:
        with open(file, "r"):
            pass
        return True
    except (FileNotFoundError, OSError):
        return False


def check_date_in_range(date1: Union[str, datetime.datetime],
                        valid_dates: int = VALID_YEARS) -> bool:
    """
    check if date is valid and in the range according to the rule we have set
    """
    now_year = datetime.datetime.now().year
    if isinstance(date1, str):
        try:
            check_date = datetime.datetime.strptime(date1, "%m-%d-%Y")
        except ValueError:
            return False
    else:
        check_date = date1
    if check_date.year > now_year + valid_dates or \
       check_date.year < now_year - valid_dates:
        return False
    return True


def check_validity_of_txt(row: str) -> bool:
    """Check if the row contains valid data"""
    get_values = re.findall(r"^(\w{" + str(EVENT_HEADER_NOT_EMPTY) + "," +
                            str(EVENT_HEADER_LIMIT) + r"})\,\s(\w{0," +
                            str(EVENT_CONTENT_LIMIT) +
                            r"})\,\s(\d{2}\-\d{2}\-\d{4})$", row)
    if get_values:
        if len(get_values[0]) == NUM_OF_VALUES:
            return True
    return False


def before_import_checking(file: str) -> bool:
    """
    checking before importing that the file exist, the file extension and
    the size meet the rules we have set.
    """
    if not is_file_exist(file):
        return False
    if not check_file_extension(file):
        return False
    if not check_file_size(file):
        return False
    return True


def after_import_checking(calendar1: List[Dict[str, Union[str, Any]]],
                          max_event_start_date: int
                          = MAX_EVENTS_START_DATE) -> bool:
    """
    checking after importing that there is no larger quantity of events
    with the same date according to the rule we have set.
    """
    same_date_counter = 1
    date_n_count = {}
    for event in calendar1:
        if event["Date"] in date_n_count:
            date_n_count[event["Date"]] += 1
            if date_n_count[event["Date"]] > same_date_counter:
                same_date_counter = date_n_count[event["Date"]]
        else:
            date_n_count[event["Date"]] = 1
    return same_date_counter <= max_event_start_date


def import_txt_file(txt_file: str) -> List[Dict[str, Union[str, Any]]]:
    calendar_content = []
    with open(txt_file, "r") as text:
        events = text.readlines()
    for event in events:
        if not check_validity_of_txt(event):
            return list()
        head, content, event_date = event.split(", ")
        if not check_date_in_range(event_date.replace("\n", "")):
            return list()
        event_date = datetime.datetime.strptime(event_date.replace("\n", ""),
                                                "%m-%d-%Y")
        calendar_content.append({"Head": head,
                                 "Content": content,
                                 "Date": event_date})
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
                   not check_date_in_range(component.get('dtstart').dt):
                    return list()
                else:
                    calendar_content.append({
                        "Head": str(component.get('summary')),
                        "Content": str(component.get('description')),
                        "Date": component.get('dtstart').dt
                        .replace(tzinfo=None)
                    })
    return calendar_content


def move_events_to_db(events: List[Dict[str, Union[str, Any]]],
                      user_id: int,
                      session: SessionLocal = SessionLocal()) -> None:
    """insert the events into Event table"""
    for event in events:
        event = Event(
            title=event["Head"],
            content=event["Content"],
            date=event["Date"],
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
    if before_import_checking(file):
        if file.lower().endswith(VALID_FILE_EXTENSION[-1]):
            import_file = import_ics_file(file)
        else:
            import_file = import_txt_file(file)
        if import_file:
            if after_import_checking(import_file):
                move_events_to_db(import_file, user_id, session)
                return "Import success"
    return "Import failed"
