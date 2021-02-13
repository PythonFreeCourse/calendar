from sqlalchemy.orm import Session

from app.database.models import User, OutOfOffice


def get_who_is_out_of_office(session: Session,
                             event_start_date,
                             invited_emails):
    """
    This func check who is out of office
    :param session: db session
    :param event_start_date: event start date
    :param invited_emails: invited users
    :return: all users that cant be at the meeting
    """
    out_of_office_users = session.query(User.username, User.email).join(OutOfOffice).filter(
        User.email.in_(invited_emails)).filter(OutOfOffice.start_date <= event_start_date,
                                               OutOfOffice.end_date >= event_start_date).filter(
        OutOfOffice.status == 'On').all()
    return out_of_office_users
