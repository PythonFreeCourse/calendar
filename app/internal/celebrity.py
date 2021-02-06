import datetime


def get_today_month_and_day() -> str:
    """Get today's month and day - %m-%d"""

    return datetime.date.today().strftime("%m-%d")