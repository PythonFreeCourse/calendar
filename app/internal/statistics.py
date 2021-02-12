from collections import namedtuple
import datetime
from typing import Dict, Tuple, Union

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.database.models import Event, UserEvent
from app.routers.user import does_user_exist, get_users

SUCCESS_STATUS = 0
ERROR_STATUS = -1
INVALID_DATE_RANGE = "End date must be later than start date"
INVALID_USER = "Invalid user id"
NIN_IN_DAY = 1440


def validate_input(
        db: Session, userid: int, start: datetime.datetime,
        end: datetime.datetime,
) -> Tuple[bool, str, datetime.datetime, datetime.datetime]:
    """ 1. input validations:
            valid userid.
            end date > start date.
        2. date range preparation:
            start: will be at 00:00 on input date (today if None).
            end: will be at 23:59:59 on input date (today if None).
    All statistics are based on full days (00:00:00-23:59:59).

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: NamedTuple with the following data:
        valid_input: boolean stating if input values are valid.
        error_text: str (relevant ib case of error).
        start: start of date range.
        end: end of date range.
    """
    Result = namedtuple(
        'result', ['valid_input', 'error_text', 'start', 'end'])
    if not does_user_exist(session=db, user_id=userid):
        return Result(False, INVALID_USER, start, end)
    date = start or datetime.datetime.now()
    start = datetime.datetime(date.year, date.month, date.day)
    single_day = datetime.timedelta(days=1, seconds=-1)
    date = end or start
    end = datetime.datetime(date.year, date.month, date.day) + single_day
    if start >= end:
        return Result(False, INVALID_DATE_RANGE, start, end)
    return Result(True, "", start, end)


def get_events_count_stats(
        db: Session, userid: int, start: datetime.datetime,
        end: datetime.datetime) -> Dict[str, Dict[str, int]]:
    """ calculate statistics and events relevant for the requested user
        and the requested date range.
        all logic is performed in the db.

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: json with
        events_count_stats: (for requested date range).
            meetings_for_user: events that the user has.
            created_by_user: events that the user has created.
    """
    meetings_for_user = db.query(Event.id).join(
        UserEvent, UserEvent.event_id == Event.id).filter(
        UserEvent.user_id == userid).filter(
        or_(
            and_(Event.start >= start, Event.start <= end),
            and_(Event.end >= start, Event.end <= end),
            and_(Event.start <= start, Event.end >= end))).count()
    created_by_user = db.query(Event.id).filter(
        Event.owner_id == userid).filter(
        or_(
            and_(Event.start >= start, Event.start <= end),
            and_(Event.end >= start, Event.end <= end),
            and_(Event.start <= start, Event.end >= end))).count()
    return {"events_count_stats": {"meetings_for_user": meetings_for_user,
                                   "created_by_user": created_by_user}}


def get_daily_events_statistics(
        db: Session, userid: int, start: datetime.datetime,
        end: datetime.datetime) -> Dict[str, Dict[str, int]]:
    """ calculate statistics for daily events relevant for the requested user
        and the requested date range.
        part of the logic is performed in the db,
        while the rest is in the code.

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: json with
        day_events_stats: (for requested date range).
            min_events_in_day: minimum number of daily events the user has.
            max_events_in_day: maximum number of daily events the user has.
            avg_events_in_day: average number of daily events the user has.
    """
    events_by_date = db.query(
        func.date(Event.start), func.count(func.date(Event.start))).join(
        UserEvent, UserEvent.event_id == Event.id).filter(
        UserEvent.user_id == userid).filter(
        or_(
            and_(Event.start >= start, Event.start <= end),
            and_(Event.end >= start, Event.end <= end),
            and_(Event.start <= start, Event.end >= end))).group_by(
        func.date(Event.start)).all()
    num_of_days_in_period = (end - start).days + 1
    if len(events_by_date) > 0:
        min_events_in_day = min(day[1] for day in events_by_date)
        max_events_in_day = max(day[1] for day in events_by_date)
        sum_events_per_period = sum(day[1] for day in events_by_date)
    else:
        min_events_in_day = 0
        max_events_in_day = 0
        sum_events_per_period = 0
    if num_of_days_in_period > len(events_by_date):
        min_events_in_day = 0
    return {"day_events_stats": {"min_events_in_day": min_events_in_day,
                                 "max_events_in_day": max_events_in_day,
                                 "avg_events_per_day":
                                     round(sum_events_per_period /
                                           num_of_days_in_period, 2)}}


def get_events_duration_statistics(
        db: Session, userid: int, start: datetime.datetime,
        end: datetime.datetime) -> Dict[str, Dict[str, int]]:
    """ calculate statistics for events durations relevant for
        the requested user and the requested date range.
        all logic is performed in the db, while the rest is in the code.

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: json with
        events_duration_statistics: (for requested date range, in minutes).
            shortest_event: shortest event the user has.
            longest_event: longest event the user has.
            average_event: average event the user has.
    """
    events_duration_statistics = db.query(
        (func.min(func.julianday(Event.end) - func.julianday(Event.start))
         * NIN_IN_DAY),
        (func.max(func.julianday(Event.end) - func.julianday(Event.start))
         * NIN_IN_DAY),
        (func.avg(func.julianday(Event.end) - func.julianday(Event.start))
         * NIN_IN_DAY)
    ).join(UserEvent, UserEvent.event_id == Event.id).filter(
        UserEvent.user_id == userid).filter(
        or_(
            and_(Event.start >= start, Event.start <= end),
            and_(Event.end >= start, Event.end <= end),
            and_(Event.start <= start, Event.end >= end))).all()
    if events_duration_statistics[0][0]:
        return {"events_duration_statistics":
                {"shortest_event": round(events_duration_statistics[0][0]),
                    "longest_event": round(events_duration_statistics[0][1]),
                    "average_event": round(events_duration_statistics[0][2])}}
    return {"events_duration_statistics":
            {"shortest_event": 0, "longest_event": 0, "average_event": 0}}


def get_participants_statistics(
        db: Session, userid: int, start: datetime.datetime,
        end: datetime.datetime) -> Dict[str, Dict[str, Union[str, int]]]:
    """ calculate statistics for events participants relevant for
        the requested user and the requested date range.
        part of the logic is performed in the db,
        while the rest is in the code.

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: json with
        max_events: maximum number of events the user has
            with same participant.
        participant_name: relevant participant name.
    """
    subquery = db.query(
        Event.id).join(UserEvent, UserEvent.event_id == Event.id).filter(
        UserEvent.user_id == userid).filter(
        or_(
            and_(Event.start >= start, Event.start <= end),
            and_(Event.end >= start, Event.end <= end),
            and_(Event.start <= start, Event.end >= end))).subquery()
    event_participants = db.query(
        UserEvent.user_id, func.count(UserEvent.user_id)).filter(
        UserEvent.user_id != userid).filter(
        UserEvent.event_id.in_(subquery)).group_by(
        UserEvent.user_id).order_by(
        func.count(UserEvent.user_id).desc()).first()
    if event_participants:
        return {
            "participants_statistics": {
                "max_events": event_participants[1],
                "participant_name": get_users(
                    db, id=event_participants[0])[0].username}}
    return {"participants_statistics": {"max_events": 0,
                                        "participant_name": ""}}


def prepare_display_text(
        output: Dict[str, Dict[str, Union[datetime.datetime, int, str]]],
        start: datetime.datetime, end: datetime.datetime
) -> Dict[str, Dict[str, str]]:
    """ prepare display text per each statistics.
        text summary for front end to display.

    Args:
        output: data calculated by other functions.
        start: start of date range.
        end: end of date range.

    Returns:
        input json + new section.
    """
    display_text = {"display_text": {
        "title": f"Statistics for {start.date()} - {end.date()}",
        "stat_1": f"You have "
                  f"{output['events_count_stats']['meetings_for_user']} "
                  f"events, {output['events_count_stats']['created_by_user']} "
                  f"you've created.",
        "stat_2":
            f"Number of daily events: "
            f"{output['day_events_stats']['min_events_in_day']} - "
            f"{output['day_events_stats']['max_events_in_day']}"
            f" events per day. Average of "
            f"{output['day_events_stats']['avg_events_per_day']}"
            f" events per day",
        "stat_3": f"Shortest event is "
                  f"{output['events_duration_statistics']['shortest_event']} "
                  f"minutes, longest is "
                  f"{output['events_duration_statistics']['longest_event']} "
                  f"minutes with an average event of "
                  f"{output['events_duration_statistics']['average_event']} "
                  f"minutes",
        "stat_4": f"Max events with the same person ("
                  f"{output['participants_statistics']['participant_name']}) "
                  f"is {output['participants_statistics']['max_events']}"}}
    return display_text


def get_statistics(
        db: Session, userid: int, start: datetime.datetime = None,
        end: datetime.datetime = None) -> Dict[str, str]:
    """ calculate statistics for user and date-range - main function.

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns: dictionary with the following entries:
        1. events_count_stats: (for requested date range).
            meetings_for_user: events that the user has.
            created_by_user: events that the user has created.
        2. day_events_stats: (for requested date range).
            min_events_in_day: minimum number of daily events the user has.
            max_events_in_day: maximum number of daily events the user has.
            avg_events_in_day: average number of daily events the user has.
        3. events_duration_statistics: (for requested date range, in minutes).
            shortest_event: shortest event the user has.
            longest_event: longest event the user has.
            average_event: average event the user has.
        4. participants_statistics: (for requested date range).
            max_events: maximum number of events the user has
                with same participant.
            participant_name: relevant participant name.
        5. display_text: (summary text to display in calendar).
            title: display title.
            stat_1: display summary for "events_count_stats".
            stat_2: display summary for "day_events_stats".
            stat_3: display summary for "events_duration_statistics".
            stat_4: display summary for "participants_statistics".
    """
    output = {}
    valid_input, error_text, start, end = validate_input(
        db, userid, start, end)
    if not valid_input:
        output["start"] = start
        output["end"] = end
        output["Status"] = ERROR_STATUS
        output["ErrorDescription"] = error_text
        return output
    output["Status"] = SUCCESS_STATUS
    output["ErrorDescription"] = ""
    output.update(get_events_count_stats(db, userid, start, end))
    output.update(get_daily_events_statistics(db, userid, start, end))
    output.update(get_events_duration_statistics(db, userid, start, end))
    output.update(get_participants_statistics(db, userid, start, end))
    output.update(prepare_display_text(output, start, end))
    return output
