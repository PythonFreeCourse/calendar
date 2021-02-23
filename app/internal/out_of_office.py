from datetime import datetime
from sqlalchemy.orm import Session
from typing import List

from app.database.models import User, OutOfOffice

DATETIME_FORMAT = "%Y-%m-%d %H:%M"
START_DATE = "start_date"
END_DATE = "end_date"
START_TIME = "start_time"
END_TIME = "end_time"


def get_who_is_out_of_office(
    session: Session,
    event_start_date: datetime,
    invited_emails: List[str],
):
    """
    Get who is out of office

    Args:
        session: db session
        event_start_date: event start date
        invited_emails: invited emails

    Returns:
        Users who are out of office at the event date
    """
    out_of_office_users = (
        session.query(User.username, User.email)
        .join(OutOfOffice)
        .filter(User.email.in_(invited_emails))
        .filter(
            OutOfOffice.start_date <= event_start_date,
            OutOfOffice.end_date >= event_start_date,
        )
        .filter(OutOfOffice.status == "On")
        .all()
    )
    return out_of_office_users


def insert_new_out_of_office(out_of_office_data, user: User, session: Session):
    out = get_out_of_office_template(
        user_id=user.id,
        start_date=get_date_formatted(
            out_of_office_data,
            START_DATE,
            START_TIME,
            DATETIME_FORMAT,
        ),
        end_date=get_date_formatted(
            out_of_office_data,
            END_DATE,
            END_TIME,
            DATETIME_FORMAT,
        ),
        status="On",
    )
    session.add(out)


def get_out_of_office_template(
    user_id,
    start_date=None,
    end_date=None,
    status="Off",
):
    return OutOfOffice(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


def get_date_formatted(out_of_office_data, date, time, date_format):
    return datetime.strptime(
        out_of_office_data[date] + " " + out_of_office_data[time],
        date_format,
    )


def update_out_of_office(
    out_of_office_data_from_req,
    out_of_office_data_from_db,
):
    activate_out_of_office = "1"

    if out_of_office_data_from_req["outOfOffice"] == activate_out_of_office:
        out_of_office_data_from_db.start_date = get_date_formatted(
            out_of_office_data_from_req,
            START_DATE,
            START_TIME,
            DATETIME_FORMAT,
        )
        out_of_office_data_from_db.end_date = get_date_formatted(
            out_of_office_data_from_req,
            END_DATE,
            END_TIME,
            DATETIME_FORMAT,
        )
        out_of_office_data_from_db.status = "On"
    else:
        out_of_office_data_from_db.status = "Off"


def update_out_of_office_status_to_off(out_of_office_data, session: Session):
    """
    Update out of office status to off if out of office date passed

    Args:
        out_of_office_data: Out of office data from db
        session: db session

    Returns:
        out_of_office_data object
    """
    if out_of_office_data:
        if out_of_office_data.status == "On":
            if out_of_office_data.end_date < datetime.now():
                out_of_office_data.status = "Off"
                session.commit()
    return out_of_office_data
