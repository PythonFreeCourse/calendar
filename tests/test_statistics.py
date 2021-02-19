import datetime

from app.internal.statistics import get_statistics
from app.internal.statistics import INVALID_DATE_RANGE, INVALID_USER
from app.internal.statistics import SUCCESS_STATUS
from app.routers.event import create_event
from app.routers.user import create_user
from app.routers.share import send_in_app_invitation, accept
from app.routers.invitation import get_all_invitations


def create_events_and_user_events(session, start, end, owner, invitations):
    for _ in range(1, 3):
        event = create_event(
            db=session, title="title" + str(_), start=start, end=end,
            owner_id=owner, location="location" + str(_))
        send_in_app_invitation(invitations, event, session)


def create_data(session):
    _ = [create_user("user" + str(_), "password" + str(_),
                     "email" + str(_) + '@' + 'gmail.com', "Hebrew",
                     session) for _ in range(1, 4)]
    start = datetime.datetime.now() + datetime.timedelta(hours=-1)
    end = datetime.datetime.now() + datetime.timedelta(hours=1)
    create_events_and_user_events(session, start, end, 1,
                                  ["email2@gmail.com", "email3@gmail.com"])
    start = datetime.datetime.now() + datetime.timedelta(days=-1)
    end = datetime.datetime.now() + datetime.timedelta(days=-1, hours=2)
    create_events_and_user_events(session, start, end, 1,
                                  ["email2@gmail.com", "email3@gmail.com"])
    start = datetime.datetime.now() + datetime.timedelta(hours=1)
    end = datetime.datetime.now() + datetime.timedelta(hours=1.5)
    create_events_and_user_events(session, start, end, 2,
                                  ["email3@gmail.com"])
    for invitation in get_all_invitations(session):
        accept(invitation, session)


def test_statistics_invalid_date_range(session):
    create_data(session)
    start = datetime.datetime.now() + datetime.timedelta(days=-2)
    end = datetime.datetime.now() + datetime.timedelta(days=-3)
    statistics = get_statistics(session, 1, start, end)
    assert statistics["error_description"] == INVALID_DATE_RANGE


def test_statistics_invalid_user(session):
    start = datetime.datetime.now()
    end = datetime.datetime.now() + datetime.timedelta(minutes=50)
    statistics = get_statistics(session, 666, start, end)
    assert statistics["error_description"] == INVALID_USER


def test_statistics_no_date_input(session):
    create_data(session)
    statistics = get_statistics(db=session, userid=1, start=None, end=None)
    assert statistics["status"] == SUCCESS_STATUS


def test_statistics_no_data_for_date_range(session):
    create_data(session)
    start = datetime.datetime.now() + datetime.timedelta(days=-20)
    end = datetime.datetime.now() + datetime.timedelta(days=-18, hours=1)
    statistics = get_statistics(session, 1, start, end)
    assert statistics["status"] == SUCCESS_STATUS


def test_statistics_success(session):
    create_data(session)
    start = datetime.datetime.now() + datetime.timedelta(days=-2)
    end = datetime.datetime.now() + datetime.timedelta(days=2, hours=1)
    statistics = get_statistics(session, 1, start, end)
    assert statistics["status"] == SUCCESS_STATUS
