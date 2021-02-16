from datetime import datetime
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


def insert_new_out_of_office(out_of_office_data_from_req,
                             user,
                             session):
    out = get_out_of_office_template(1,
                                     user_id=user.id,
                                     start_date=datetime.strptime(
                                         out_of_office_data_from_req['start_date'] + ' ' +
                                         out_of_office_data_from_req['start_time'],
                                         '%Y-%m-%d %H:%M'),
                                     end_date=datetime.strptime(out_of_office_data_from_req['end_date'] + ' ' +
                                                                out_of_office_data_from_req['end_time'],
                                                                '%Y-%m-%d %H:%M'),
                                     status='On')
    session.add(out)


def get_out_of_office_template(out_of_office_id, user_id, start_date=None, end_date=None, status='Off'):
    return OutOfOffice(
        id=out_of_office_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status=status
    )


def update_out_of_office(out_of_office_data_from_req, out_of_office_data_from_db):
    activate_out_of_office = 1
    if out_of_office_data_from_req['outOfOffice'] == activate_out_of_office:
        out_of_office_data_from_db.start_date = datetime.strptime(
            out_of_office_data_from_req['start_date'] + ' ' + out_of_office_data_from_req['start_time'],
            '%Y-%m-%d %H:%M')
        out_of_office_data_from_db.end_date = datetime.strptime(
            out_of_office_data_from_req['end_date'] + ' ' + out_of_office_data_from_req['end_time'],
            '%Y-%m-%d %H:%M')
        out_of_office_data_from_db.status = 'On'
    else:
        out_of_office_data_from_db.status = 'Off'


def update_out_of_office_status_to_off_if_the_time_is_pass(out_of_office_data, session):
    """
    This func check if out of office date passed and changed the status to off
    :param out_of_office_data: Out of office data from db
    :param session:
    :return: out_of_office_data object
    """
    if out_of_office_data:
        if out_of_office_data.status == 'On':
            if out_of_office_data.end_date < datetime.now():
                # update status to off
                out_of_office_data.status = 'Off'
                session.commit()
    return out_of_office_data


def get_out_of_office_template():
    return OutOfOffice(id=1,
                       user_id=1,
                       start_date='',
                       end_date='',
                       status='Off')
