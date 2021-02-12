import re
from datetime import datetime, timedelta

from app.database.models import User, Event, UserEvent
from sqlalchemy.orm import Session
from typing import List, Match

REGEX_EXTRACT_HOLIDAYS = re.compile(
    r'SUMMARY:(?P<title>.*)(\n.*){1,8}DTSTAMP:(?P<date>\w{8})',
    re.MULTILINE)


def get_holidays_from_file(file: List[Event], session: Session) -> List[Event]:
    """
    This function using regex to extract holiday title
    and date from standrd ics file
    :param file:standard ics file
    :param session:current connection
    :return:list of holidays events
    """
    parsed_holidays = REGEX_EXTRACT_HOLIDAYS.finditer(file)
    holidays = []
    for holiday in parsed_holidays:
        holiday_event = create_holiday_event(
            holiday, session.query(User).filter_by(id=1).first().id)
        holidays.append(holiday_event)
    return holidays


def create_holiday_event(holiday: Match[str], owner_id: int) -> Event:
    valid_ascii_chars_range = 128
    title = holiday.groupdict()['title'].strip()
    title_to_save = ''.join(i if ord(i) < valid_ascii_chars_range
                            else '' for i in title)
    date = holiday.groupdict()['date'].strip()
    format_string = '%Y%m%d'
    holiday = Event(
        title=title_to_save,
        start=datetime.strptime(date, format_string),
        end=datetime.strptime(date, format_string) + timedelta(days=1),
        content='holiday',
        owner_id=owner_id
    )
    return holiday


def save_holidays_to_db(holidays: List[Event], session: Session):
    """
    this function saves holiday list into database.
    :param holidays: list of holidays events
    :param session: current connection
    """
    session.add_all(holidays)
    session.commit()
    session.flush(holidays)
    userevents = []
    for holiday in holidays:
        userevent = UserEvent(
            user_id=holiday.owner_id,
            event_id=holiday.id
        )
        userevents.append(userevent)
    session.add_all(userevents)
    session.commit()
