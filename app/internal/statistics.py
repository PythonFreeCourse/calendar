import datetime
from typing import Dict, List, NamedTuple, Tuple, Union

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from sqlalchemy.util import symbol

from app.database.models import Event, UserEvent
from app.routers.user import does_user_exist, get_users

SUCCESS_STATUS = True
ERROR_STATUS = False
INVALID_DATE_RANGE = "End date must be later than start date"
INVALID_USER = "Invalid user id"
NIN_IN_DAY = 1440

ValidationResult = NamedTuple(
    "ValidationResult",
    [
        ("valid_input", bool),
        ("error_text", str),
        ("start", datetime.datetime),
        ("end", datetime.datetime),
    ],
)
DailyEventsStatistics = NamedTuple(
    "DailyEventsStatistics",
    [
        ("min_events_in_day", int),
        ("max_events_in_day", int),
        ("avg_events_per_day", float),
    ],
)
EventsDurationStatistics = NamedTuple(
    "EventsDurationStatistics",
    [
        ("shortest_event", float),
        ("longest_event", float),
        ("average_event", float),
    ],
)


def validate_input(
        db: Session,
        userid: int,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
) -> ValidationResult:
    """1. input validations:
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
    if not does_user_exist(session=db, user_id=userid):
        return ValidationResult(
            valid_input=False,
            error_text=INVALID_USER,
            start=start,
            end=end,
        )
    date = start or datetime.datetime.now()
    start = datetime.datetime(date.year, date.month, date.day)
    single_day = datetime.timedelta(days=1, seconds=-1)
    date = end or start
    end = datetime.datetime(date.year, date.month, date.day) + single_day
    if start >= end:
        return ValidationResult(
            valid_input=False,
            error_text=INVALID_DATE_RANGE,
            start=start,
            end=end,
        )
    return ValidationResult(
        valid_input=True, error_text="", start=start, end=end
    )


def get_date_filter_between_dates(
    start: datetime.datetime, end: datetime.datetime
) -> symbol:
    """
    Prepare the filter by dates using declarative SQLAlchemy.

    Returns:
        concatenated sql part for events date as sqlalchemy.util.symbol
    """
    event_start, event_end = func.date(Event.start), func.date(Event.end)
    return or_(
        and_(event_start >= start, event_start <= end),
        and_(event_end >= start, event_end <= end),
        and_(event_start <= start, event_end >= end),
    )


def get_events_count_stats(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> Dict[str, Dict[str, int]]:
    """calculate statistics and events relevant for the requested user
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
    user_to_event = (UserEvent, UserEvent.event_id == Event.id)
    by_user_id = UserEvent.user_id == userid
    by_owner_id = Event.owner_id == userid
    meetings_for_user = (
        db
        .query(Event.id)
        .join(user_to_event)
        .filter(by_user_id)
        .filter(get_date_filter_between_dates(start, end))
        .count()
    )
    created_by_user = (
        db
        .query(Event.id)
        .filter(by_owner_id)
        .filter(get_date_filter_between_dates(start, end))
        .count()
    )
    return {
        "events_count_stats": {
            "meetings_for_user": meetings_for_user,
            "created_by_user": created_by_user,
        }
    }


def get_events_by_date(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> List[Tuple[datetime.datetime, int]]:
    """get date + number of events on it

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns:
        data of date + number of events on it.
    """
    start_date = func.date(Event.start)
    events_count = func.count(start_date)
    by_user_id = UserEvent.user_id == userid
    user_to_event = (UserEvent, UserEvent.event_id == Event.id)
    return (
        db
        .query(start_date, events_count)
        .join(user_to_event)
        .filter(by_user_id)
        .filter(get_date_filter_between_dates(start, end))
        .all()
    )


def calc_daily_events_statistics(
    events_by_date: List[Tuple[datetime.datetime, int]],
    start: datetime.datetime,
    end: datetime.datetime,
) -> DailyEventsStatistics:
    """go over sets of data retrieved from the db and calculate:
            minimum, maximum and average number of daily events
    Args:
        events_by_date: data of date + number of events on it from the
            get_events_by_date function
        start: start of date range.
        end: end of date range.

    Returns:
        NamedTuple of:
            min_events_in_day, max_events_in_day, avg_events_per_day
    """
    num_of_days_in_period = (end - start).days + 1
    min_events_in_day = min(day[1] for day in events_by_date)
    max_events_in_day = max(day[1] for day in events_by_date)
    sum_events_per_period = sum(day[1] for day in events_by_date)
    if num_of_days_in_period > len(events_by_date):
        min_events_in_day = 0
    avg_events_per_day = round(
        sum_events_per_period / num_of_days_in_period, 2
    )
    return DailyEventsStatistics(
        min_events_in_day, max_events_in_day, avg_events_per_day
    )


def get_daily_events_statistics(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> Dict[str, Dict[str, int]]:
    """calculate statistics for daily events relevant for the requested user
        and the requested date range. logic is performed in:
        the db (get_events_by_date function),
        while the rest is in the code (calc_daily_events_statistics function).

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
    events_by_date = get_events_by_date(db, userid, start, end)
    daily_events_statistics = calc_daily_events_statistics(
        events_by_date, start, end
    )
    return {
        "day_events_stats": {
            "min_events_in_day": daily_events_statistics.min_events_in_day,
            "max_events_in_day": daily_events_statistics.max_events_in_day,
            "avg_events_per_day": daily_events_statistics.avg_events_per_day,
        }
    }


def get_events_duration_statistics_from_db(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> EventsDurationStatistics:
    """get data of shortest, longest and average event duration from the db

    Args:
        db: db session.
        userid: requested user id number for statistics.
        start: start of date range.
        end: end of date range.

    Returns:
        NamedTuple of: shortest_event, longest_event, average_event
    """
    event_duration = func.julianday(Event.end) - func.julianday(Event.start)
    user_to_event = (UserEvent, UserEvent.event_id == Event.id)
    by_user_id = UserEvent.user_id == userid
    events_duration_statistics = (
        db
        .query(
            (func.min(event_duration) * NIN_IN_DAY),
            (func.max(event_duration) * NIN_IN_DAY),
            (func.avg(event_duration) * NIN_IN_DAY),
        )
        .join(user_to_event)
        .filter(by_user_id)
        .filter(get_date_filter_between_dates(start, end))
        .all()
    )
    if events_duration_statistics[0][0]:
        return EventsDurationStatistics(
            shortest_event=round(events_duration_statistics[0][0]),
            longest_event=round(events_duration_statistics[0][1]),
            average_event=round(events_duration_statistics[0][2]),
        )
    return EventsDurationStatistics(
        shortest_event=0, longest_event=0, average_event=0
    )


def get_events_duration_statistics(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> Dict[str, Dict[str, float]]:
    """calculate statistics for events durations relevant for
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
    events_duration_statistics = get_events_duration_statistics_from_db(
        db, userid, start, end,
    )
    return {
        "events_duration_statistics": {
            "shortest_event": events_duration_statistics.shortest_event,
            "longest_event": events_duration_statistics.longest_event,
            "average_event": events_duration_statistics.average_event,
        }
    }


def get_participants_statistics(
        db: Session,
        userid: int,
        start: datetime.datetime,
        end: datetime.datetime,
) -> Dict[str, Dict[str, Union[str, int]]]:
    """calculate statistics for events participants relevant for
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
    by_user_id = UserEvent.user_id == userid
    by_not_user_id = UserEvent.user_id != userid
    user_to_event = (UserEvent, UserEvent.event_id == Event.id)
    participant_count = func.count(UserEvent.user_id)
    subquery = (
        db
        .query(Event.id)
        .join(user_to_event)
        .filter(by_user_id)
        .filter(get_date_filter_between_dates(start, end))
        .subquery()
    )
    event_participants = (
        db
        .query(UserEvent.user_id, participant_count)
        .filter(by_not_user_id)
        .filter(UserEvent.event_id.in_(subquery))
        .group_by(UserEvent.user_id)
        .order_by(participant_count.desc())
        .first()
    )
    if event_participants:
        return {
            "participants_statistics": {
                "max_events": event_participants[1],
                "participant_name": get_users(
                    db, id=event_participants[0]
                )[0].username,
            }
        }
    return {
        "participants_statistics": {"max_events": 0, "participant_name": ""}
    }


def prepare_display_text(
    output: Dict[str, Dict[str, Union[datetime.datetime, int, str]]],
    start: datetime.datetime,
    end: datetime.datetime,
) -> Dict[str, Dict[str, str]]:
    """prepare display text per each statistics.
        text summary for front end to display.

    Args:
        output: data calculated by other functions.
        start: start of date range.
        end: end of date range.

    Returns:
        input json + new section.
    """
    display_text = {
        "display_text": {
            "title": f"Statistics for {start.date()} - {end.date()}",
            "stat_1": f"You have "
            f"{output['events_count_stats']['meetings_for_user']} "
            f"events, {output['events_count_stats']['created_by_user']}"
            f" you've created.",
            "stat_2": f"Number of daily events: "
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
            f"is {output['participants_statistics']['max_events']}",
        }
    }
    return display_text


def update_output(output, *params) -> Dict[str, Union[str, bool]]:
    """fetch all statistics by calling relevant functions:
            1. several functions for calculating statistics (1 per each area)
            2. function for preparing the display summary

    Args:
        output: dictionary
        list of parameters:
        params[0] - db: db session.
        params[1] - userid: requested user id number for statistics.
        params[2] - start: start of date range.
        params[3] - end: end of date range.

    Returns:
        dictionary with statistics
    """
    call_functions = [
        get_events_count_stats,
        get_daily_events_statistics,
        get_events_duration_statistics,
        get_participants_statistics,
    ]
    for call_function in call_functions:
        output.update(call_function(*params))
    output.update(prepare_display_text(
        output,
        start=params[2],
        end=params[3],
    ))
    return output


def get_statistics(
    db: Session,
    userid: int,
    start: datetime.datetime = None,
    end: datetime.datetime = None,
) -> Dict[str, Union[str, bool]]:
    """calculate statistics for user and date-range - main function.

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
    params = [db, userid, start, end]
    validate_result = validate_input(*params)
    if not validate_result.valid_input:
        output["start"] = validate_result.start
        output["end"] = validate_result.end
        output["status"] = ERROR_STATUS
        output["error_description"] = validate_result.error_text
        return output
    output["status"] = SUCCESS_STATUS
    output["error_description"] = ""
    params = [db, userid, validate_result.start, validate_result.end]
    output = update_output(output, *params)
    return output
